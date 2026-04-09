import streamlit as st
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import get_db
from crawler.douban_spider import fetch_comments
from analysis.data_cleaner import clean_dataframe
from analysis.nlp_processor import (
    analyze_sentiment_distribution,
    compute_avg_sentiment_score,
    get_word_frequency,
    get_daily_comment_count
)
from config.settings import FONT_PATH

from pyecharts.charts import Pie, Line
from pyecharts import options as opts
from streamlit_echarts import st_pyecharts
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(page_title="豆瓣电影舆情分析", layout="wide")

st.title("豆瓣电影短评舆情分析平台")

db = get_db()

movie_id = st.text_input("请输入豆瓣电影 ID（如 35267232）", value="")

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
                        st.error("采集失败，可能需要登录 Cookie 或网络受限")
                        st.stop()
                    st.success(f"采集完成，共获取 {total} 条评论")
                except Exception as e:
                    st.error(f"采集异常: {e}")
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
                font_path = FONT_PATH if os.path.exists(FONT_PATH) else None
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