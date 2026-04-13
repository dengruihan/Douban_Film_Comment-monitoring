import streamlit as st
import pandas as pd
import os
import sys
import platform
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import get_db
from crawler.douban_spider import fetch_comments, search_movie
from analysis.data_cleaner import clean_dataframe
from analysis.nlp_processor import (
    analyze_sentiment_distribution,
    compute_avg_sentiment_score,
    get_word_frequency,
    get_daily_comment_count,
)
from config.settings import FONT_PATH


def get_chinese_font_path():
    """
    获取中文字体路径

    优先级：
    1. 项目字体文件
    2. 系统字体

    Returns:
        str or None: 字体路径，未找到返回None
    """
    # 优先使用项目字体
    if os.path.exists(FONT_PATH):
        return FONT_PATH

    # 使用系统字体
    system = platform.system()

    if system == "Darwin":  # macOS
        system_fonts = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
        ]
    elif system == "Windows":
        system_fonts = [
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simsun.ttc",
        ]
    elif system == "Linux":
        system_fonts = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        ]
    else:
        return None

    # 查找第一个存在的系统字体
    for font in system_fonts:
        if os.path.exists(font):
            return font

    return None


from pyecharts.charts import Pie, Line
from pyecharts import options as opts
from streamlit_echarts import st_pyecharts
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(page_title="豆瓣电影舆情分析", layout="wide")

st.title("豆瓣电影短评舆情分析平台")

db = get_db()

movie_id = None

# 电影搜索
movie_name = st.text_input(
    "请输入电影名称（如：肖申克的救赎）", value="", placeholder="输入电影名进行搜索..."
)

if movie_name:
    with st.spinner("正在搜索电影..."):
        search_results = search_movie(movie_name)

    if search_results:
        st.success(f"找到 {len(search_results)} 部相关电影")

        # 构建选项列表
        options = []
        for item in search_results:
            year_str = f"({item['year']})" if item["year"] else ""
            rating_str = f"评分: {item['rating']}"
            label = f"{item['title']} {year_str} - {rating_str}"
            options.append(label)

        selected = st.selectbox("请选择要分析的电影", options)
        selected_index = options.index(selected)
        movie_id = search_results[selected_index]["movie_id"]

        st.info(
            f"✅ 已选择：{search_results[selected_index]['title']} (ID: {movie_id})"
        )
    elif movie_name:
        st.warning("未找到相关电影，请尝试其他关键词")

if "analyzed_movie_id" not in st.session_state:
    st.session_state.analyzed_movie_id = None

if st.button("开始分析"):
    if not movie_id:
        st.error("请输入有效的电影 ID")
    else:
        st.session_state.analyzed_movie_id = movie_id

if (
    st.session_state.analyzed_movie_id
    and st.session_state.analyzed_movie_id == movie_id
):
    existing_count = db.comment_count(movie_id)
    movie_info = db.get_movie_info(movie_id)

    if existing_count > 0:
        col_info, col_refresh = st.columns([3, 1])
        with col_info:
            updated_at = movie_info.get("updated_at", "未知") if movie_info else "未知"
            st.info(f"📊 数据库已有 {existing_count} 条评论 | 最后更新：{updated_at}")
        with col_refresh:
            if st.button("🔄 刷新数据", help="删除旧数据并重新采集最新评论"):
                with st.spinner("正在删除旧数据..."):
                    db.delete_movie_data(movie_id)
                st.session_state.analyzed_movie_id = movie_id
                st.rerun()
    else:
        progress_bar = st.progress(0, text="正在准备采集评论数据...")

        class CrawlState:
            def __init__(self):
                self.lock = threading.Lock()
                self.completed_pages = 0
                self.total_pages = 0
                self.total_count = 0
                self.page_count = 0
                self.fetching = False
                self.done = False
                self.error = None
                self.result = None

        crawl_state = CrawlState()

        def on_progress(
            current_page, total_pages, page_count, total_count, phase="complete"
        ):
            with crawl_state.lock:
                crawl_state.total_pages = total_pages
                crawl_state.total_count = total_count
                if phase == "fetching":
                    crawl_state.completed_pages = current_page
                    crawl_state.fetching = True
                elif phase == "complete":
                    crawl_state.completed_pages = current_page
                    crawl_state.fetching = False
                    crawl_state.page_count = page_count

        def run_fetch():
            try:
                total = fetch_comments(movie_id, progress_callback=on_progress)
                with crawl_state.lock:
                    crawl_state.result = total
                    crawl_state.done = True
            except Exception as e:
                with crawl_state.lock:
                    crawl_state.error = e
                    crawl_state.done = True

        thread = threading.Thread(target=run_fetch, daemon=True)
        thread.start()

        displayed = 0.0
        while True:
            with crawl_state.lock:
                completed = crawl_state.completed_pages
                total_pages = crawl_state.total_pages
                fetching = crawl_state.fetching
                total_count = crawl_state.total_count
                page_count = crawl_state.page_count
                is_done = crawl_state.done
                error = crawl_state.error

            if is_done:
                break

            if total_pages > 0:
                base = completed / total_pages
                target = (completed + 1) / total_pages if fetching else base
                if displayed < base:
                    displayed = base
                if displayed < target:
                    displayed = min(
                        displayed + (target - base) * 0.015 + 0.0003, target
                    )

                if completed == 0 and fetching:
                    label = f"正在采集评论数据... 第 1/{total_pages} 页"
                elif page_count > 0 and not fetching:
                    label = f"正在采集评论数据... 第 {completed}/{total_pages} 页 | 本页 {page_count} 条 | 累计 {total_count} 条"
                else:
                    label = f"正在采集评论数据... 第 {completed + 1}/{total_pages} 页 | 累计 {total_count} 条"

                progress_bar.progress(displayed, text=label)

            time.sleep(0.05)

        thread.join()

        if error:
            progress_bar.empty()
            import traceback

            error_detail = traceback.format_exc()
            st.error(f"采集异常: {str(error)}")
            with st.expander("查看详细错误信息"):
                st.code(error_detail)
            st.info(
                "💡 如果问题持续，可以尝试：\n1. 检查网络连接\n2. 更换其他电影\n3. 稍后再试"
            )
            st.session_state.analyzed_movie_id = None
            st.stop()

        total = crawl_state.result
        if total == 0:
            progress_bar.empty()
            st.error("采集失败，未获取到评论数据")
            st.info(
                "💡 可能原因：\n1. 电影ID不存在\n2. 该电影暂无评论\n3. 网络连接问题"
            )
            st.session_state.analyzed_movie_id = None
            st.stop()

        progress_bar.progress(1.0, text=f"采集完成！共获取 {total} 条评论")
        st.success(f"采集完成，共获取 {total} 条评论")

    comments = db.get_comments(movie_id)
    if not comments:
        st.warning("没有评论数据")
        st.session_state.analyzed_movie_id = None
        st.stop()

    movie_info = db.get_movie_info(movie_id)
    if movie_info:
        st.subheader(
            f"电影：{movie_info.get('movie_name', '未知')} | 平均评分：{movie_info.get('avg_rating', 'N/A')}"
        )

    df = pd.DataFrame(comments)
    df = clean_dataframe(df)

    if df.empty:
        st.warning("清洗后无有效评论数据")
        st.session_state.analyzed_movie_id = None
        st.stop()

    sentiment_dist = analyze_sentiment_distribution(df)
    avg_score = compute_avg_sentiment_score(df)
    total_count = len(df)
    pos_rate = sentiment_dist["正面"] / total_count * 100 if total_count > 0 else 0
    pos_weighted_rate = sentiment_dist.get("正面_加权", 0)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("评论总数", total_count)
    with col2:
        st.metric("好评率", f"{pos_rate:.1f}%")
    with col3:
        st.metric(
            "加权好评率",
            f"{pos_weighted_rate:.1f}%",
            help="考虑星级、点赞数和情感强度的加权好评率",
        )
    with col4:
        st.metric("平均情感得分", f"{avg_score:.2f}")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("情感分布")

        show_weighted = st.checkbox(
            "显示加权分布",
            value=False,
            help="加权分布考虑了评论的星级、点赞数和情感强度",
        )

        if show_weighted:
            pos_w = sentiment_dist.get("正面_加权", 0)
            neu_w = sentiment_dist.get("中性_加权", 0)
            neg_w = sentiment_dist.get("负面_加权", 0)
            pie_data = [
                ("正面", round(pos_w, 1)),
                ("中性", round(neu_w, 1)),
                ("负面", round(neg_w, 1)),
            ]
            title_suffix = "（加权）"
        else:
            pie_data = [
                ("正面", sentiment_dist["正面"]),
                ("中性", sentiment_dist["中性"]),
                ("负面", sentiment_dist["负面"]),
            ]
            title_suffix = ""

        pie = (
            Pie()
            .add(
                "",
                pie_data,
                radius=["30%", "70%"],
                label_opts=opts.LabelOpts(formatter="{b}: {c} ({d}%)"),
            )
            .set_global_opts(title_opts=opts.TitleOpts(title=""))
            .set_colors(["#67C23A", "#E6A23C", "#F56C6C"])
        )
        st_pyecharts(pie)

    with col_right:
        st.subheader("高频词云")

        use_ai_filter = st.checkbox(
            "使用AI智能筛选关键词",
            value=True,
            help="AI筛选可以过滤无意义词汇，保留真正的关键词",
        )

        word_freq = get_word_frequency(df, top_n=100)
        if word_freq:
            from analysis.nlp_processor import smart_filter_keywords

            filtered_keywords = smart_filter_keywords(
                word_freq, top_n=50, use_ai=use_ai_filter
            )

            word_dict = {}
            for keyword in filtered_keywords:
                for word, count in word_freq:
                    if word == keyword:
                        word_dict[word] = count
                        break

            if not word_dict:
                st.warning("关键词筛选后无有效词汇")
            else:
                font_path = get_chinese_font_path()

                if font_path is None:
                    st.warning(
                        "未找到中文字体，词云可能显示为方块。请安装中文字体或添加字体文件到assets目录。"
                    )

                try:
                    wc = WordCloud(
                        font_path=font_path,
                        width=800,
                        height=400,
                        background_color="white",
                        max_words=50,
                    )
                    wc.generate_from_frequencies(word_dict)
                    fig, ax = plt.subplots(figsize=(8, 4))
                    ax.imshow(wc, interpolation="bilinear")
                    ax.axis("off")
                    st.pyplot(fig)

                    filter_method = "AI智能筛选" if use_ai_filter else "正则表达式筛选"
                    st.caption(
                        f"筛选方式: {filter_method} | 关键词数量: {len(word_dict)}"
                    )
                except Exception as e:
                    st.error(f"词云生成失败: {e}")
                    st.info("提示：可能缺少中文字体支持")
        else:
            st.info("无足够词汇生成词云")

    st.markdown("---")
    st.subheader("评论热度时间轴")

    daily_df = get_daily_comment_count(df)
    if not daily_df.empty:
        dates = [str(d) for d in daily_df["date"]]
        counts = daily_df["count"].tolist()
        line = (
            Line()
            .add_xaxis(dates)
            .add_yaxis("评论数", counts, is_smooth=True)
            .set_global_opts(
                title_opts=opts.TitleOpts(title=""),
                xaxis_opts=opts.AxisOpts(type_="category"),
                yaxis_opts=opts.AxisOpts(type_="value"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
            )
        )
        st_pyecharts(line)
    else:
        st.info("无有效时间数据")

    st.markdown("---")
    st.subheader("评论详情")

    sort_by = st.radio(
        "排序方式",
        ["按权重排序（推荐）", "按点赞数排序", "按时间排序"],
        horizontal=True,
        help="权重排序综合考虑星级、点赞数和情感强度",
    )

    df_display = df.copy()
    weights = []
    for i in df_display.index:
        star_rating = df_display.loc[i, "star_rating"]
        vote_count = df_display.loc[i, "vote_count"]
        text = df_display.loc[i, "comment_text"]

        from analysis.nlp_processor import compute_sentiment, calculate_comment_weight

        _, sentiment_score = compute_sentiment(text, star_rating)
        weight = calculate_comment_weight(star_rating, vote_count, sentiment_score)
        weights.append(weight)

    df_display["weight"] = weights

    if sort_by == "按权重排序（推荐）":
        df_display = df_display.sort_values("weight", ascending=False)
    elif sort_by == "按点赞数排序":
        df_display = df_display.sort_values("vote_count", ascending=False)
    else:
        df_display["comment_time"] = pd.to_datetime(
            df_display["comment_time"], errors="coerce"
        )
        df_display = df_display.sort_values("comment_time", ascending=False)

    display_df = df_display[
        [
            "user_name",
            "star_rating",
            "comment_text",
            "vote_count",
            "weight",
            "comment_time",
        ]
    ].head(50)
    display_df.columns = ["用户", "星级", "评论", "点赞数", "权重", "时间"]

    display_df["权重"] = display_df["权重"].apply(lambda x: f"{x:.2f}")

    st.dataframe(display_df, width="stretch")

    st.markdown("---")
    st.subheader("同类电影对比")

    movie_info = db.get_movie_info(movie_id)
    genres = (
        movie_info.get("genres", "").split(",")
        if movie_info and movie_info.get("genres")
        else []
    )

    if not genres:
        st.info("暂无该电影的分类信息，无法进行同类对比")
    else:
        st.caption(f"当前电影分类：{'、'.join(genres)}")

        similar_movies = []
        for genre in genres:
            found = db.get_movies_by_genre(genre, exclude_movie_id=movie_id)
            for m in found:
                if not any(x["movie_id"] == m["movie_id"] for x in similar_movies):
                    similar_movies.append(m)

        if not similar_movies:
            st.info(
                "数据库中暂无同类电影数据。分析其他同类电影后，这里将自动显示对比图表。"
            )
        else:
            current_dist = sentiment_dist
            current_total = len(df)

            compare_data = [
                {
                    "名称": movie_info.get("movie_name", "当前电影"),
                    "movie_id": movie_id,
                    "豆瓣评分": movie_info.get("avg_rating", 0),
                    "好评率": round(current_dist["正面"] / current_total * 100, 1)
                    if current_total
                    else 0,
                    "加权好评率": round(current_dist.get("正面_加权", 0), 1),
                    "评论数": current_total,
                }
            ]

            for m in similar_movies:
                m_comments = db.get_comments(m["movie_id"])
                if not m_comments:
                    continue
                m_df = pd.DataFrame(m_comments)
                m_df = clean_dataframe(m_df)
                if m_df.empty:
                    continue
                m_dist = analyze_sentiment_distribution(m_df)
                m_total = len(m_df)
                compare_data.append(
                    {
                        "名称": m["movie_name"],
                        "movie_id": m["movie_id"],
                        "豆瓣评分": m["avg_rating"],
                        "好评率": round(m_dist["正面"] / m_total * 100, 1)
                        if m_total
                        else 0,
                        "加权好评率": round(m_dist.get("正面_加权", 0), 1),
                        "评论数": m_total,
                    }
                )

            compare_df = pd.DataFrame(compare_data)

            from pyecharts.charts import Bar

            movie_names = compare_df["名称"].tolist()

            bar = (
                Bar()
                .add_xaxis(movie_names)
                .add_yaxis("好评率 (%)", compare_df["好评率"].tolist(), color="#67C23A")
                .add_yaxis(
                    "加权好评率 (%)", compare_df["加权好评率"].tolist(), color="#409EFF"
                )
                .set_global_opts(
                    title_opts=opts.TitleOpts(title="同类电影好评率对比"),
                    tooltip_opts=opts.TooltipOpts(trigger="axis"),
                    yaxis_opts=opts.AxisOpts(max_=100),
                )
            )
            st_pyecharts(bar)

            st.dataframe(
                compare_df[["名称", "豆瓣评分", "好评率", "加权好评率", "评论数"]],
                width="stretch",
            )
