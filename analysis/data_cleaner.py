import re
import pandas as pd


def clean_text(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'@[\w\u4e00-\u9fff]+', '', text)
    text = re.sub(r'[^\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\w\s,.!?;:\'"()\-]', '', text)
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def clean_dataframe(df):
    df = df.copy()
    df['comment_text'] = df['comment_text'].apply(clean_text)
    df = df[df['comment_text'].str.len() >= 2]
    df = df.reset_index(drop=True)
    return df
