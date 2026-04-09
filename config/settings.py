MAX_PAGES = 10  # 每页20条评论，10页=200条（推荐值，避免被封禁）
# 如需更多评论可调整为 20（400条）或 50（1000条），但爬取时间会更长
REQUEST_DELAY_RANGE = (3, 6)
MAX_RETRIES = 3
DB_PATH = "database/sentiment.db"
SENTIMENT_THRESHOLD_POS = 0.6
SENTIMENT_THRESHOLD_NEG = 0.4
LOG_DIR = "logs"
LOG_FILE = "logs/crawler.log"
STOPWORDS_PATH = "assets/stopwords.txt"
FONT_PATH = "assets/simhei.ttf"
COMMENTS_PER_PAGE = 20
BASE_URL = "https://movie.douban.com/subject/{movie_id}/comments"
MOVIE_URL = "https://movie.douban.com/subject/{movie_id}"
