import streamlit as st
import pandas as pd
import os
import sys
import platform

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import get_db
from crawler.douban_spider import fetch_comments, search_movie
from analysis.data_cleaner import clean_dataframe
from analysis.nlp_processor import (
    analyze_sentiment_distribution,
    compute_avg_sentiment_score,
    get_word_frequency,
    get_daily_comment_count
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
            "/System/Library/Fonts/Hiragino Sans GB.ttc"
        ]
    elif system == "Windows":
        system_fonts = [
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simsun.ttc"
        ]
    elif system == "Linux":
        system_fonts = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
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

# 搜索方式选择
search_mode = st.radio("选择输入方式", ["电影名搜索", "直接输入电影ID"], horizontal=True)

movie_id = None

if search_mode == "电影名搜索":
    movie_name = st.text_input("请输入电影名称（如：肖申克的救赎）", value="")

    if movie_name:
        with st.spinner("正在搜索电影..."):
            search_results = search_movie(movie_name)

        if search_results:
            st.success(f"找到 {len(search_results)} 部相关电影")

            # 构建选项列表
            options = []
            for item in search_results:
                year_str = f"({item['year']})" if item['year'] else ""
                rating_str = f"评分: {item['rating']}"
                label = f"{item['title']} {year_str} - {rating_str}"
                options.append(label)

            selected = st.selectbox("请选择要分析的电影", options)
            selected_index = options.index(selected)
            movie_id = search_results[selected_index]['movie_id']

            st.info(f"✅ 已选择：{search_results[selected_index]['title']} (ID: {movie_id})")
        elif movie_name:
            st.warning("未找到相关电影，请尝试其他关键词或使用电影ID直接输入")

else:
    movie_id = st.text_input("请输入豆瓣电影 ID（如 1292052）", value="")

if st.button("开始分析"):
    if not movie_id:
        st.error("请输入有效的电影 ID")
    else:
        existing_count = db.comment_count(movie_id)
        if existing_count > 0:
            st.info(f"数据库已有 {existing_count} 条评论，直接进行分析")
        else:
            with st.spinner("正在采集评论数据，请耐心等待..."):
                try:
                    total = fetch_comments(movie_id)
                    if total == 0:
                        st.error("采集失败，未获取到评论数据")
                        st.info("💡 可能原因：\n1. 电影ID不存在\n2. 该电影暂无评论\n3. 网络连接问题")
                        st.stop()
                    st.success(f"采集完成，共获取 {total} 条评论")
                except Exception as e:
                    import traceback
                    error_detail = traceback.format_exc()
                    st.error(f"采集异常: {str(e)}")
                    with st.expander("查看详细错误信息"):
                        st.code(error_detail)
                    st.info("💡 如果问题持续，可以尝试：\n1. 检查网络连接\n2. 更换其他电影\n3. 稍后再试")
                    st.stop()

        comments = db.get_comments(movie_id)
        if not comments:
            st.warning("没有评论数据")
            st.stop()

        movie_info = db.get_movie_info(movie_id)
        if movie_info:
            st.subheader(f"电影：{movie_info.get('movie_name', '未知')} | 平均评分：{movie_info.get('avg_rating', 'N/A')}")

        df = pd.DataFrame(comments)
        df = clean_dataframe(df)

        if df.empty:
            st.warning("清洗后无有效评论数据")
            st.stop()

        sentiment_dist = analyze_sentiment_distribution(df)
        avg_score = compute_avg_sentiment_score(df)
        total_count = len(df)
        pos_rate = sentiment_dist["正面"] / total_count * 100 if total_count > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("评论总数", total_count)
        with col2:
            st.metric("好评率", f"{pos_rate:.1f}%")
        with col3:
            st.metric("平均情感得分", f"{avg_score:.2f}")

        st.markdown("---")

        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("情感分布")
            pie_data = [
                ("正面", sentiment_dist["正面"]),
                ("中性", sentiment_dist["中性"]),
                ("负面", sentiment_dist["负面"])
            ]
            pie = (
                Pie()
                .add(
                    "",
                    pie_data,
                    radius=["30%", "70%"],
                    label_opts=opts.LabelOpts(formatter="{b}: {c} ({d}%)")
                )
                .set_global_opts(title_opts=opts.TitleOpts(title=""))
                .set_colors(["#67C23A", "#E6A23C", "#F56C6C"])
            )
            st_pyecharts(pie)

        with col_right:
            st.subheader("高频词云")
            word_freq = get_word_frequency(df, top_n=100)
            if word_freq:
                word_dict = {word: count for word, count in word_freq}
                font_path = get_chinese_font_path()
                
                if font_path is None:
                    st.warning("未找到中文字体，词云可能显示为方块。请安装中文字体或添加字体文件到assets目录。")
                
                try:
                    wc = WordCloud(
                        font_path=font_path,
                        width=800,
                        height=400,
                        background_color="white",
                        max_words=100
                    )
                    wc.generate_from_frequencies(word_dict)
                    fig, ax = plt.subplots(figsize=(8, 4))
                    ax.imshow(wc, interpolation="bilinear")
                    ax.axis("off")
                    st.pyplot(fig)
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
                    tooltip_opts=opts.TooltipOpts(trigger="axis")
                )
            )
            st_pyecharts(line)
        else:
            st.info("无有效时间数据")

        st.markdown("---")
        st.subheader("评论详情（前 50 条）")
        display_df = df[["user_name", "star_rating", "comment_text", "vote_count", "comment_time"]].head(50)
        display_df.columns = ["用户", "星级", "评论", "有用数", "时间"]
        st.dataframe(display_df, use_container_width=True)