import jieba
import jieba.posseg as pseg
import pandas as pd
import os
import re
import logging
from collections import Counter
from snownlp import SnowNLP
from config.settings import STOPWORDS_PATH, SENTIMENT_THRESHOLD_POS, SENTIMENT_THRESHOLD_NEG
from analysis.data_cleaner import clean_dataframe

logger = logging.getLogger(__name__)


def load_stopwords():
    if not os.path.exists(STOPWORDS_PATH):
        return set()
    with open(STOPWORDS_PATH, 'r', encoding='utf-8') as f:
        stopwords = set(line.strip() for line in f if line.strip())
    return stopwords


def segment_words(text, stopwords_set):
    words = jieba.cut(text, cut_all=False)
    filtered = [w for w in words if len(w) >= 2 and w not in stopwords_set]
    return filtered


def compute_sentiment(text, star_rating=None):
    """
    计算评论的情感倾向

    优先级：
    1. 星级评分（1-2星=负面，5星=正面，3-4星=中性或结合文本）
    2. 文本情感分析

    Args:
        text: 评论文本
        star_rating: 星级评分（1-5）

    Returns:
        tuple: (情感标签, 情感得分)
        - 情感标签: "正面"、"中性"、"负面"
        - 情感得分: 0-1之间的浮点数
    """
    sentiment_score = 0.5  # 默认中性

    # 优先使用星级判断（星级是用户明确表达的情感倾向）
    if star_rating is not None and not pd.isna(star_rating):
        star_rating = int(star_rating)
        # 1-2星明确为负面
        if star_rating in (1, 2):
            sentiment_score = 0.2 if star_rating == 1 else 0.3
            return "负面", sentiment_score
        # 5星明确为正面
        if star_rating == 5:
            sentiment_score = 0.9
            return "正面", sentiment_score
        # 3-4星为中性，但可结合文本分析进行细化
        if star_rating in (3, 4):
            # 如果文本足够长，使用SnowNLP辅助判断
            if len(text) >= 5:
                try:
                    sentiment_score = SnowNLP(text).sentiments
                    if sentiment_score > SENTIMENT_THRESHOLD_POS:
                        return "正面", sentiment_score
                    if sentiment_score < SENTIMENT_THRESHOLD_NEG:
                        return "负面", sentiment_score
                except Exception:
                    pass
            sentiment_score = 0.5 if star_rating == 3 else 0.6
            return "中性", sentiment_score

    # 无星级时，过短评论返回中性
    if len(text) < 5:
        return "中性", 0.5

    # 无星级时使用SnowNLP进行情感分析
    try:
        sentiment_score = SnowNLP(text).sentiments
    except Exception:
        return "中性", 0.5

    if sentiment_score > SENTIMENT_THRESHOLD_POS:
        return "正面", sentiment_score
    if sentiment_score < SENTIMENT_THRESHOLD_NEG:
        return "负面", sentiment_score
    return "中性", sentiment_score


def calculate_comment_weight(star_rating, vote_count, sentiment_score):
    """
    计算评论权重

    权重维度：
    1. 星级权重：极端评价（1星/5星）权重高，中性评价（3星）权重低
    2. 点赞权重：高点赞评论权重高
    3. 情感强度权重：情感越强烈权重越高

    Args:
        star_rating: 星级评分（1-5）
        vote_count: 点赞数
        sentiment_score: 情感得分（0-1）

    Returns:
        float: 综合权重
    """
    import math

    # 1. 星级权重：|星级 - 3|
    if star_rating is not None and not pd.isna(star_rating):
        star_weight = abs(int(star_rating) - 3)
    else:
        star_weight = 0

    # 2. 点赞权重：log(点赞数 + 1)
    vote_weight = math.log(vote_count + 1)

    # 3. 情感强度权重：|情感得分 - 0.5| * 2
    sentiment_intensity = abs(sentiment_score - 0.5) * 2

    # 综合权重：(星级权重 + 1) * (点赞权重 + 1) * (情感强度 + 0.5)
    weight = (star_weight + 1) * (vote_weight + 1) * (sentiment_intensity + 0.5)

    return weight


def get_word_frequency(df, top_n=100):
    stopwords = load_stopwords()
    all_words = []
    for text in df['comment_text']:
        words = segment_words(text, stopwords)
        all_words.extend(words)
    counter = Counter(all_words)
    return counter.most_common(top_n)


def regex_filter_keywords(word_list, top_n=50):
    """
    使用正则表达式和词性筛选关键词（降级方案）

    Args:
        word_list: 词频列表 [(词, 频次), ...]
        top_n: 返回前N个关键词

    Returns:
        list: 筛选后的关键词列表
    """
    # 扩展停用词
    extended_stopwords = {
        '觉得', '感觉', '真的', '非常', '特别', '就是', '这个', '那个',
        '什么', '怎么', '还是', '可以', '已经', '一直', '一个', '没有',
        '这样', '那样', '这么', '那么', '因为', '所以', '但是', '如果',
        '虽然', '然后', '而且', '或者', '不过', '只是', '还有', '也是'
    }

    # 无意义词汇模式
    meaningless_patterns = [
        r'^[一-龥]$',      # 单字
        r'^\d+$',          # 纯数字
        r'^[a-zA-Z]$',     # 单字母
        r'^[的了吗呢吧啊哦嗯]$',  # 语气词
    ]

    filtered = []
    for word, count in word_list:
        # 停用词过滤
        if word in extended_stopwords:
            continue

        # 正则过滤
        if any(re.match(p, word) for p in meaningless_patterns):
            continue

        # 词性过滤（保留名词、动词、形容词）
        try:
            words = pseg.cut(word)
            for w, flag in words:
                # n: 名词, v: 动词, a: 形容词, nr: 人名, ns: 地名
                if flag.startswith(('n', 'v', 'a')):
                    filtered.append(word)
                    break
        except Exception:
            # 词性分析失败，保守保留
            filtered.append(word)

    logger.info(f"正则筛选：{len(word_list)} -> {len(filtered)} 个关键词")
    return filtered[:top_n]


def smart_filter_keywords(word_list, top_n=50, use_ai=True):
    """
    智能筛选关键词（AI优先，正则降级）

    Args:
        word_list: 词频列表 [(词, 频次), ...]
        top_n: 返回前N个关键词
        use_ai: 是否使用AI筛选

    Returns:
        list: 筛选后的关键词列表
    """
    if use_ai:
        try:
            from analysis.ai_client import ai_filter_keywords
            logger.info("尝试使用AI筛选关键词...")
            keywords = ai_filter_keywords(word_list, top_n)
            if keywords and len(keywords) > 0:
                logger.info(f"AI筛选成功，返回 {len(keywords)} 个关键词")
                return keywords
            else:
                logger.warning("AI筛选返回空结果，降级到正则筛选")
        except Exception as e:
            logger.warning(f"AI筛选失败: {e}，降级到正则筛选")

    # 降级到正则筛选
    logger.info("使用正则表达式筛选关键词...")
    return regex_filter_keywords(word_list, top_n)


def analyze_sentiment_distribution(df):
    """
    分析情感分布（支持加权）

    Args:
        df: 评论数据框

    Returns:
        dict: 包含计数和加权占比的情感分布
    """
    pos_count = 0
    neu_count = 0
    neg_count = 0
    pos_weight = 0.0
    neu_weight = 0.0
    neg_weight = 0.0
    total_weight = 0.0

    for i in df.index:
        text = df.loc[i, 'comment_text']
        star_rating = df.loc[i, 'star_rating']
        vote_count = df.loc[i, 'vote_count']

        # 计算情感和权重
        label, sentiment_score = compute_sentiment(text, star_rating)
        weight = calculate_comment_weight(star_rating, vote_count, sentiment_score)

        # 统计计数
        if label == "正面":
            pos_count += 1
            pos_weight += weight
        elif label == "中性":
            neu_count += 1
            neu_weight += weight
        else:
            neg_count += 1
            neg_weight += weight

        total_weight += weight

    # 计算加权占比
    if total_weight > 0:
        pos_weighted_pct = (pos_weight / total_weight) * 100
        neu_weighted_pct = (neu_weight / total_weight) * 100
        neg_weighted_pct = (neg_weight / total_weight) * 100
    else:
        pos_weighted_pct = neu_weighted_pct = neg_weighted_pct = 0

    return {
        "正面": pos_count,
        "中性": neu_count,
        "负面": neg_count,
        "正面_加权": pos_weighted_pct,
        "中性_加权": neu_weighted_pct,
        "负面_加权": neg_weighted_pct
    }


def compute_avg_sentiment_score(df):
    if df.empty:
        return 0.0
    scores = []
    for text in df['comment_text']:
        try:
            score = SnowNLP(text).sentiments
            scores.append(score)
        except Exception:
            continue
    if not scores:
        return 0.0
    return sum(scores) / len(scores)


def get_daily_comment_count(df):
    df = df.copy()
    df['comment_time'] = pd.to_datetime(df['comment_time'], errors='coerce')
    df = df.dropna(subset=['comment_time'])
    df['date'] = df['comment_time'].dt.date
    result = df.groupby('date').size().reset_index(name='count')
    result.columns = ['date', 'count']
    result = result.sort_values('date').reset_index(drop=True)
    return result
