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


def search_movie(movie_name):
    """
    根据电影名搜索豆瓣电影（使用移动端API）

    Args:
        movie_name: 电影名称

    Returns:
        list: 搜索结果列表，每项包含 {movie_id, title, rating, year}
    """
    from urllib.parse import quote

    url = f'https://m.douban.com/rexxar/api/v2/search/movie?q={quote(movie_name)}&count=10'
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
        'Referer': 'https://m.douban.com/'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = []
            for item in data.get('items', []):
                if item.get('target_type') == 'movie':
                    target = item.get('target', {})
                    rating_info = target.get('rating', {})
                    rating_value = rating_info.get('value', 0)

                    # 格式化评分显示
                    if rating_value > 0:
                        rating_str = str(rating_value)
                    else:
                        rating_str = "暂无评分"

                    results.append({
                        "movie_id": target.get('id'),
                        "title": target.get('title'),
                        "rating": rating_str,
                        "year": target.get('year', '')
                    })
            return results
        else:
            logger.warning(f"搜索电影失败，状态码: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"搜索电影异常: {e}")
        return []


def fetch_movie_info(movie_id):
    """使用移动端API获取电影信息（含分类）"""
    url = f'https://m.douban.com/rexxar/api/v2/movie/{movie_id}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
        'Referer': 'https://m.douban.com/'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            rating_info = data.get('rating', {})
            return {
                "movie_name": data.get('title', '未知'),
                "avg_rating": rating_info.get('value', 0.0) if rating_info else 0.0,
                "genres": data.get('genres', [])
            }
        else:
            logger.warning(f"获取电影信息失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"获取电影信息异常: {e}")
        return None


def fetch_comments(movie_id, max_pages=None, progress_callback=None):
    """
    使用移动端API获取评论（无需Cookie）

    Args:
        movie_id: 豆瓣电影ID
        max_pages: 最大采集页数
        progress_callback: 进度回调函数 callback(current_page, total_pages, page_count, total_count)
    """
    if max_pages is None:
        max_pages = MAX_PAGES
    db = get_db()
    total_comments = 0

    # 获取电影信息（允许失败，不影响评论采集）
    try:
        movie_info = fetch_movie_info(movie_id)
        if movie_info:
            db.insert_movie_info(
                movie_id,
                movie_info["movie_name"],
                movie_info["avg_rating"],
                movie_info.get("genres", [])
            )
        else:
            logger.warning("电影信息获取失败，但继续采集评论")
    except Exception as e:
        logger.error(f"获取电影信息异常: {e}，但继续采集评论")

    if progress_callback:
        progress_callback(0, max_pages, 0, 0, 'fetching')

    for page in range(max_pages):
        if progress_callback:
            progress_callback(page, max_pages, 0, total_comments, 'fetching')
        start = page * COMMENTS_PER_PAGE
        url = f'https://m.douban.com/rexxar/api/v2/movie/{movie_id}/interests?count={COMMENTS_PER_PAGE}&order_by=hot&start={start}&for_mobile=1'
        result = _fetch_page_mobile(url, movie_id)
        if result is None:
            logger.warning(f"第 {page + 1} 页返回失败，停止采集")
            break
        if not result:
            logger.info(f"第 {page + 1} 页无更多评论，停止采集")
            break
        db.insert_comments(result)
        total_comments += len(result)
        logger.info(f"第 {page + 1}/{max_pages} 页采集完成，本页 {len(result)} 条评论，累计 {total_comments} 条")
        if progress_callback:
            progress_callback(page + 1, max_pages, len(result), total_comments, 'complete')
        time.sleep(random.uniform(*REQUEST_DELAY_RANGE))

    return total_comments


def _fetch_page_mobile(url, movie_id, retry_count=0):
    """
    使用移动端API获取评论页面
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
        'Referer': f'https://m.douban.com/movie/subject/{movie_id}/'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            interests = data.get('interests', [])
            if not interests:
                return []

            comments = []
            for item in interests:
                user = item.get('user', {})
                rating_info = item.get('rating')

                # 处理rating可能为None的情况
                if rating_info is None:
                    star_rating = 0
                else:
                    star_rating = rating_info.get('star_count', 0)

                comments.append({
                    "movie_id": movie_id,
                    "user_name": user.get('name', '匿名') if user else '匿名',
                    "star_rating": star_rating,
                    "comment_text": item.get('comment', ''),
                    "vote_count": item.get('vote_count', 0),
                    "comment_time": item.get('create_time', '')
                })
            return comments
        elif response.status_code == 403:
            logger.warning("API访问受限")
            return None
        else:
            logger.warning(f"请求失败，状态码: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        if retry_count < MAX_RETRIES:
            logger.warning(f"请求异常: {e}，第 {retry_count + 1} 次重试")
            time.sleep(5)
            return _fetch_page_mobile(url, movie_id, retry_count=retry_count + 1)
        else:
            logger.error(f"请求异常: {e}，已达最大重试次数 {MAX_RETRIES}")
            return None
