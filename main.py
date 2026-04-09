import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler.douban_spider import fetch_comments
from database.db_manager import get_db

def main():
    parser = argparse.ArgumentParser(description="豆瓣电影短评爬虫")
    parser.add_argument("--movie_id", required=True, help="豆瓣电影 ID")
    parser.add_argument("--max_pages", type=int, default=None, help="最大采集页数")
    args = parser.parse_args()

    movie_id = args.movie_id
    max_pages = args.max_pages

    print(f"开始采集电影 {movie_id} 的短评...")
    try:
        total = fetch_comments(movie_id, max_pages=max_pages)
        print(f"采集完成，共获取 {total} 条评论")
        db = get_db()
        count = db.comment_count(movie_id)
        print(f"数据库中共有 {count} 条评论")
    except Exception as e:
        print(f"采集失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()