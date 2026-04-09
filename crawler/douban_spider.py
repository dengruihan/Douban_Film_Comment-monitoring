import requests
import time
import random
import logging
import os

from config.settings import MAX_PAGES, REQUEST_DELAY_RANGE, MAX_RETRIES, COMMENTS_PER_PAGE, BASE_URL, MOVIE_URL, LOG_FILE, LOG_DIR
from config.headers import get_random_headers
from crawler.parser import parse_comments, parse_movie_info
from database.db_manager import get_db

os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("douban_spider")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def fetch_movie_info(movie_id):
    url = MOVIE_URL.format(movie_id=movie_id)
    headers = get_random_headers()
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return parse_movie_info(response.text)
        else:
            logger.warning(f"获取电影信息失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"获取电影信息异常: {e}")
        return None


def fetch_comments(movie_id, max_pages=None):
    if max_pages is None:
        max_pages = MAX_PAGES
    db = get_db()
    total_comments = 0

    movie_info = fetch_movie_info(movie_id)
    if movie_info:
        db.insert_movie_info(movie_id, movie_info["movie_name"], movie_info["avg_rating"])

    for page in range(max_pages):
        start = page * COMMENTS_PER_PAGE
        url = BASE_URL.format(movie_id=movie_id) + f"?start={start}&limit=20&sort=new_score&status=P"
        result = _fetch_page(url)
        if result is None:
            logger.warning(f"第 {page + 1} 页返回 403，停止采集")
            break
        if not result:
            logger.info(f"第 {page + 1} 页无更多评论，停止采集")
            break
        for comment in result:
            comment["movie_id"] = movie_id
        db.insert_comments(result)
        total_comments += len(result)
        logger.info(f"第 {page + 1}/{max_pages} 页采集完成，本页 {len(result)} 条评论，累计 {total_comments} 条")
        time.sleep(random.uniform(*REQUEST_DELAY_RANGE))

    return total_comments


def _fetch_page(url, retry_count=0):
    headers = get_random_headers()
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return parse_comments(response.text)
        elif response.status_code == 403:
            logger.warning("需要登录Cookie")
            return None
        elif response.status_code == 418:
            if retry_count < MAX_RETRIES:
                logger.warning(f"状态码 418，第 {retry_count + 1} 次重试，休眠 60 秒")
                time.sleep(60)
                return _fetch_page(url, retry_count=retry_count + 1)
            else:
                logger.error(f"状态码 418，已达最大重试次数 {MAX_RETRIES}")
                return None
        else:
            logger.warning(f"请求失败，状态码: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        if retry_count < MAX_RETRIES:
            logger.warning(f"请求异常: {e}，第 {retry_count + 1} 次重试")
            return _fetch_page(url, retry_count=retry_count + 1)
        else:
            logger.error(f"请求异常: {e}，已达最大重试次数 {MAX_RETRIES}")
            return None
