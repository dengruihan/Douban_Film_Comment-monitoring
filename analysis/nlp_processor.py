import jieba
import pandas as pd
import os
from collections import Counter
from snownlp import SnowNLP
from config.settings import STOPWORDS_PATH, SENTIMENT_THRESHOLD_POS, SENTIMENT_THRESHOLD_NEG
from analysis.data_cleaner import clean_dataframe


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
        str: 情感标签（"正面"、"中性"、"负面"）
    """
    # 优先使用星级判断（星级是用户明确表达的情感倾向）
    if star_rating is not None and not pd.isna(star_rating):
        star_rating = int(star_rating)
        # 1-2星明确为负面
        if star_rating in (1, 2):
            return "负面"
        # 5星明确为正面
        if star_rating == 5:
            return "正面"
        # 3-4星为中性，但可结合文本分析进行细化
        if star_rating in (3, 4):
            # 如果文本足够长，使用SnowNLP辅助判断
            if len(text) >= 5:
                try:
                    score = SnowNLP(text).sentiments
                    if score > SENTIMENT_THRESHOLD_POS:
                        return "正面"
                    if score < SENTIMENT_THRESHOLD_NEG:
                        return "负面"
                except Exception:
                    pass
            return "中性"
    
    # 无星级时，过短评论返回中性
    if len(text) < 5:
        return "中性"
    
    # 无星级时使用SnowNLP进行情感分析
    try:
        score = SnowNLP(text).sentiments
    except Exception:
        return "中性"
    
    if score > SENTIMENT_THRESHOLD_POS:
        return "正面"
    if score < SENTIMENT_THRESHOLD_NEG:
        return "负面"
    return "中性"


def get_word_frequency(df, top_n=100):
    stopwords = load_stopwords()
    all_words = []
    for text in df['comment_text']:
        words = segment_words(text, stopwords)
        all_words.extend(words)
    counter = Counter(all_words)
    return counter.most_common(top_n)


def analyze_sentiment_distribution(df):
    pos_count = 0
    neu_count = 0
    neg_count = 0
    for i in df.index:
        label = compute_sentiment(df.loc[i, 'comment_text'], df.loc[i, 'star_rating'])
        if label == "正面":
            pos_count += 1
        elif label == "中性":
            neu_count += 1
        else:
            neg_count += 1
    return {"正面": pos_count, "中性": neu_count, "负面": neg_count}


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
