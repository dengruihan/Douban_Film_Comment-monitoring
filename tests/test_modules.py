import sys
sys.path.insert(0, '.')

print("=== 测试配置模块 ===")
from config.settings import MAX_PAGES, DB_PATH, SENTIMENT_THRESHOLD_POS, SENTIMENT_THRESHOLD_NEG
print(f"MAX_PAGES: {MAX_PAGES}")
print(f"DB_PATH: {DB_PATH}")
print(f"SENTIMENT_THRESHOLD_POS: {SENTIMENT_THRESHOLD_POS}")
print(f"SENTIMENT_THRESHOLD_NEG: {SENTIMENT_THRESHOLD_NEG}")

from config.headers import get_random_headers, USER_AGENTS, REFERER, COOKIE
print(f"USER_AGENTS 数量: {len(USER_AGENTS)}")
print(f"REFERER: {REFERER}")
headers = get_random_headers()
print(f"get_random_headers() 返回 keys: {list(headers.keys())}")

print("\n=== 测试数据库模块 ===")
from database.db_manager import DatabaseManager, get_db
db = get_db()
print(f"数据库连接成功: {db.db_path}")

print("\n=== 测试爬虫解析模块 ===")
from crawler.parser import parse_comments, parse_movie_info
test_html = '<div class="comment-item"><div class="comment-info"><a>测试用户</a><span class="rating allstar50"></span><span title="2024-01-01">时间</span></div><span class="short">测试评论</span><span class="votes">10</span></div>'
comments = parse_comments(test_html)
print(f"parse_comments 测试结果: {comments}")

print("\n=== 测试数据清洗模块 ===")
from analysis.data_cleaner import clean_text, clean_dataframe
test_text = "<p>这电影真不错！</p>@某人 https://xxx.com"
cleaned = clean_text(test_text)
print(f"clean_text 测试: '{cleaned}'")

print("\n=== 测试 NLP 模块 ===")
from analysis.nlp_processor import load_stopwords, compute_sentiment, segment_words
stopwords = load_stopwords()
print(f"停用词数量: {len(stopwords)}")
result1 = compute_sentiment("这电影真不错", 5)
print(f"compute_sentiment('这电影真不错', 5): {result1}")
result2 = compute_sentiment("太烂了", 1)
print(f"compute_sentiment('太烂了', 1): {result2}")
result3 = compute_sentiment("还行吧", 3)
print(f"compute_sentiment('还行吧', 3): {result3}")

print("\n=== 所有模块测试通过 ===")