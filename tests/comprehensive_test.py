#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
豆瓣电影短评舆情分析平台 - 全面功能测试
测试员：产品功能测试员
测试日期：2026-04-09
"""

import sys
import os
import sqlite3
import tempfile
import shutil

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 测试结果收集
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def log_test(test_id, test_name, status, message=""):
    """记录测试结果"""
    result = {
        "test_id": test_id,
        "test_name": test_name,
        "message": message
    }
    if status == "PASS":
        test_results["passed"].append(result)
        print(f"✓ [{test_id}] {test_name} - 通过")
    elif status == "FAIL":
        test_results["failed"].append(result)
        print(f"✗ [{test_id}] {test_name} - 失败: {message}")
    else:
        test_results["warnings"].append(result)
        print(f"⚠ [{test_id}] {test_name} - 警告: {message}")

print("=" * 80)
print("豆瓣电影短评舆情分析平台 - 功能测试报告")
print("=" * 80)
print()

# ============================================================================
# 第一部分：配置模块测试
# ============================================================================
print("=" * 80)
print("一、配置模块测试")
print("=" * 80)

try:
    from config.settings import (
        MAX_PAGES, DB_PATH, SENTIMENT_THRESHOLD_POS, 
        SENTIMENT_THRESHOLD_NEG, STOPWORDS_PATH, FONT_PATH
    )
    
    # TC-CFG-01: 配置项加载测试
    if MAX_PAGES == 10:
        log_test("TC-CFG-01", "MAX_PAGES配置", "PASS", f"值为{MAX_PAGES}")
    else:
        log_test("TC-CFG-01", "MAX_PAGES配置", "FAIL", f"期望10，实际{MAX_PAGES}")
    
    # TC-CFG-02: 情感阈值配置测试
    if SENTIMENT_THRESHOLD_POS == 0.6 and SENTIMENT_THRESHOLD_NEG == 0.4:
        log_test("TC-CFG-02", "情感阈值配置", "PASS", f"正面阈值{SENTIMENT_THRESHOLD_POS}, 负面阈值{SENTIMENT_THRESHOLD_NEG}")
    else:
        log_test("TC-CFG-02", "情感阈值配置", "FAIL", "阈值配置不正确")
    
    # TC-CFG-03: 路径配置测试
    if DB_PATH and STOPWORDS_PATH:
        log_test("TC-CFG-03", "路径配置", "PASS", f"数据库路径: {DB_PATH}")
    else:
        log_test("TC-CFG-03", "路径配置", "FAIL", "路径配置缺失")
        
except Exception as e:
    log_test("TC-CFG-01", "配置模块导入", "FAIL", str(e))

try:
    from config.headers import get_random_headers, USER_AGENTS
    
    # TC-CFG-04: Headers随机生成测试
    headers = get_random_headers()
    if "User-Agent" in headers and "Referer" in headers:
        log_test("TC-CFG-04", "Headers随机生成", "PASS", f"包含{len(headers)}个字段")
    else:
        log_test("TC-CFG-04", "Headers随机生成", "FAIL", "缺少必要字段")
    
    # TC-CFG-05: User-Agent池测试
    if len(USER_AGENTS) >= 5:
        log_test("TC-CFG-05", "User-Agent池", "PASS", f"包含{len(USER_AGENTS)}个UA")
    else:
        log_test("TC-CFG-05", "User-Agent池", "WARN", f"UA数量较少: {len(USER_AGENTS)}")
        
except Exception as e:
    log_test("TC-CFG-04", "Headers模块导入", "FAIL", str(e))

print()

# ============================================================================
# 第二部分：数据库模块测试
# ============================================================================
print("=" * 80)
print("二、数据库模块测试")
print("=" * 80)

# 创建临时数据库用于测试
temp_db_fd, temp_db_path = tempfile.mkstemp(suffix='.db')

try:
    from database.db_manager import DatabaseManager
    
    # TC-DB-01: 数据库初始化测试
    try:
        db = DatabaseManager(temp_db_path)
        if os.path.exists(temp_db_path):
            log_test("TC-DB-01", "数据库初始化", "PASS", f"数据库创建成功: {temp_db_path}")
        else:
            log_test("TC-DB-01", "数据库初始化", "FAIL", "数据库文件未创建")
    except Exception as e:
        log_test("TC-DB-01", "数据库初始化", "FAIL", str(e))
    
    # TC-DB-02: 表结构验证测试
    try:
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        # 检查movie_info表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='movie_info'")
        if cursor.fetchone():
            log_test("TC-DB-02", "movie_info表存在", "PASS")
        else:
            log_test("TC-DB-02", "movie_info表存在", "FAIL", "表不存在")
        
        # 检查movie_comments表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='movie_comments'")
        if cursor.fetchone():
            log_test("TC-DB-02", "movie_comments表存在", "PASS")
        else:
            log_test("TC-DB-02", "movie_comments表存在", "FAIL", "表不存在")
        
        conn.close()
    except Exception as e:
        log_test("TC-DB-02", "表结构验证", "FAIL", str(e))
    
    # TC-DB-03: 插入电影信息测试
    try:
        db.insert_movie_info("test_movie_001", "测试电影", 8.5)
        movie_info = db.get_movie_info("test_movie_001")
        if movie_info and movie_info["movie_name"] == "测试电影":
            log_test("TC-DB-03", "插入电影信息", "PASS", f"电影名: {movie_info['movie_name']}, 评分: {movie_info['avg_rating']}")
        else:
            log_test("TC-DB-03", "插入电影信息", "FAIL", "查询结果不匹配")
    except Exception as e:
        log_test("TC-DB-03", "插入电影信息", "FAIL", str(e))
    
    # TC-DB-04: 重复插入电影信息测试（REPLACE语义）
    try:
        db.insert_movie_info("test_movie_001", "测试电影更新", 9.0)
        movie_info = db.get_movie_info("test_movie_001")
        if movie_info and movie_info["movie_name"] == "测试电影更新" and movie_info["avg_rating"] == 9.0:
            log_test("TC-DB-04", "重复插入电影信息", "PASS", "REPLACE语义正确")
        else:
            log_test("TC-DB-04", "重复插入电影信息", "FAIL", "REPLACE语义异常")
    except Exception as e:
        log_test("TC-DB-04", "重复插入电影信息", "FAIL", str(e))
    
    # TC-DB-05: 插入评论测试
    try:
        test_comments = [
            {
                "movie_id": "test_movie_001",
                "user_name": "用户A",
                "star_rating": 5,
                "comment_text": "非常好看的电影！",
                "vote_count": 100,
                "comment_time": "2024-01-01"
            },
            {
                "movie_id": "test_movie_001",
                "user_name": "用户B",
                "star_rating": 4,
                "comment_text": "还不错",
                "vote_count": 50,
                "comment_time": "2024-01-02"
            }
        ]
        inserted = db.insert_comments(test_comments)
        if inserted == 2:
            log_test("TC-DB-05", "插入评论", "PASS", f"成功插入{inserted}条评论")
        else:
            log_test("TC-DB-05", "插入评论", "FAIL", f"期望插入2条，实际插入{inserted}条")
    except Exception as e:
        log_test("TC-DB-05", "插入评论", "FAIL", str(e))
    
    # TC-DB-06: 重复插入评论测试（UNIQUE约束）
    try:
        duplicate_comment = [{
            "movie_id": "test_movie_001",
            "user_name": "用户A",
            "star_rating": 3,
            "comment_text": "修改后的评论",
            "vote_count": 200,
            "comment_time": "2024-01-03"
        }]
        inserted = db.insert_comments(duplicate_comment)
        if inserted == 0:
            log_test("TC-DB-06", "重复插入评论", "PASS", "UNIQUE约束生效，防止重复插入")
        else:
            log_test("TC-DB-06", "重复插入评论", "FAIL", "UNIQUE约束未生效")
    except Exception as e:
        log_test("TC-DB-06", "重复插入评论", "FAIL", str(e))
    
    # TC-DB-07: 查询评论测试
    try:
        comments = db.get_comments("test_movie_001")
        if len(comments) == 2 and comments[0]["user_name"] in ["用户A", "用户B"]:
            log_test("TC-DB-07", "查询评论", "PASS", f"查询到{len(comments)}条评论")
        else:
            log_test("TC-DB-07", "查询评论", "FAIL", f"期望2条评论，实际{len(comments)}条")
    except Exception as e:
        log_test("TC-DB-07", "查询评论", "FAIL", str(e))
    
    # TC-DB-08: 评论计数测试
    try:
        count = db.comment_count("test_movie_001")
        if count == 2:
            log_test("TC-DB-08", "评论计数", "PASS", f"评论数: {count}")
        else:
            log_test("TC-DB-08", "评论计数", "FAIL", f"期望2，实际{count}")
    except Exception as e:
        log_test("TC-DB-08", "评论计数", "FAIL", str(e))
    
    # TC-DB-09: 查询不存在的电影
    try:
        movie_info = db.get_movie_info("nonexistent_movie")
        if movie_info is None:
            log_test("TC-DB-09", "查询不存在的电影", "PASS", "正确返回None")
        else:
            log_test("TC-DB-09", "查询不存在的电影", "FAIL", "应返回None")
    except Exception as e:
        log_test("TC-DB-09", "查询不存在的电影", "FAIL", str(e))
    
    # TC-DB-10: 插入空评论列表
    try:
        inserted = db.insert_comments([])
        if inserted == 0:
            log_test("TC-DB-10", "插入空评论列表", "PASS", "正确处理空列表")
        else:
            log_test("TC-DB-10", "插入空评论列表", "FAIL", "应返回0")
    except Exception as e:
        log_test("TC-DB-10", "插入空评论列表", "FAIL", str(e))
    
except Exception as e:
    log_test("TC-DB-01", "数据库模块导入", "FAIL", str(e))

print()

# ============================================================================
# 第三部分：数据清洗模块测试
# ============================================================================
print("=" * 80)
print("三、数据清洗模块测试")
print("=" * 80)

try:
    from analysis.data_cleaner import clean_text, clean_dataframe
    import pandas as pd
    
    # TC-DC-01: 清洗HTML标签
    try:
        text = "<p>这是一段评论</p><div>测试</div>"
        cleaned = clean_text(text)
        if "<p>" not in cleaned and "<div>" not in cleaned:
            log_test("TC-DC-01", "清洗HTML标签", "PASS", f"'{text}' -> '{cleaned}'")
        else:
            log_test("TC-DC-01", "清洗HTML标签", "FAIL", f"未完全清洗: '{cleaned}'")
    except Exception as e:
        log_test("TC-DC-01", "清洗HTML标签", "FAIL", str(e))
    
    # TC-DC-02: 清洗URL
    try:
        text = "这个电影不错 https://example.com/video 还有 http://test.com"
        cleaned = clean_text(text)
        if "https://" not in cleaned and "http://" not in cleaned:
            log_test("TC-DC-02", "清洗URL", "PASS", f"URL已移除")
        else:
            log_test("TC-DC-02", "清洗URL", "FAIL", f"URL未完全清洗: '{cleaned}'")
    except Exception as e:
        log_test("TC-DC-02", "清洗URL", "FAIL", str(e))
    
    # TC-DC-03: 清洗@提及
    try:
        text = "@张三 这个电影很好看 @李四 你也看看"
        cleaned = clean_text(text)
        if "@张三" not in cleaned and "@李四" not in cleaned:
            log_test("TC-DC-03", "清洗@提及", "PASS", "@提及已移除")
        else:
            log_test("TC-DC-03", "清洗@提及", "FAIL", f"@提及未完全清洗: '{cleaned}'")
    except Exception as e:
        log_test("TC-DC-03", "清洗@提及", "FAIL", str(e))
    
    # TC-DC-04: 清洗特殊字符
    try:
        text = "电影很棒！★★★☆☆【推荐】"
        cleaned = clean_text(text)
        # 应保留中文、标点等
        if "电影很棒" in cleaned:
            log_test("TC-DC-04", "清洗特殊字符", "PASS", f"'{text}' -> '{cleaned}'")
        else:
            log_test("TC-DC-04", "清洗特殊字符", "FAIL", "中文内容丢失")
    except Exception as e:
        log_test("TC-DC-04", "清洗特殊字符", "FAIL", str(e))
    
    # TC-DC-05: 清洗空白字符
    try:
        text = "这\n是\r\n一\t段  评论"
        cleaned = clean_text(text)
        if "\n" not in cleaned and "\r" not in cleaned and "\t" not in cleaned:
            log_test("TC-DC-05", "清洗空白字符", "PASS", f"换行符和制表符已处理")
        else:
            log_test("TC-DC-05", "清洗空白字符", "FAIL", f"空白字符未完全清洗: '{cleaned}'")
    except Exception as e:
        log_test("TC-DC-05", "清洗空白字符", "FAIL", str(e))
    
    # TC-DC-06: DataFrame清洗测试
    try:
        df = pd.DataFrame({
            "comment_text": [
                "<p>好的电影</p>",
                "短",
                "https://test.com 测试评论内容",
                "这是一个正常的评论内容，长度足够"
            ]
        })
        cleaned_df = clean_dataframe(df)
        # 应过滤掉长度小于2的评论
        if len(cleaned_df) == 3 and "https://" not in cleaned_df.iloc[1]["comment_text"]:
            log_test("TC-DC-06", "DataFrame清洗", "PASS", f"原始{len(df)}条，清洗后{len(cleaned_df)}条")
        else:
            log_test("TC-DC-06", "DataFrame清洗", "FAIL", f"期望3条，实际{len(cleaned_df)}条")
    except Exception as e:
        log_test("TC-DC-06", "DataFrame清洗", "FAIL", str(e))
    
    # TC-DC-07: 空文本清洗
    try:
        text = ""
        cleaned = clean_text(text)
        if cleaned == "":
            log_test("TC-DC-07", "空文本清洗", "PASS", "正确处理空文本")
        else:
            log_test("TC-DC-07", "空文本清洗", "FAIL", f"空文本应返回空字符串")
    except Exception as e:
        log_test("TC-DC-07", "空文本清洗", "FAIL", str(e))
    
except Exception as e:
    log_test("TC-DC-01", "数据清洗模块导入", "FAIL", str(e))

print()

# ============================================================================
# 第四部分：NLP情感分析模块测试
# ============================================================================
print("=" * 80)
print("四、NLP情感分析模块测试")
print("=" * 80)

try:
    from analysis.nlp_processor import (
        load_stopwords, segment_words, compute_sentiment,
        get_word_frequency, analyze_sentiment_distribution,
        compute_avg_sentiment_score, get_daily_comment_count
    )
    import pandas as pd
    
    # TC-NLP-01: 停用词加载测试
    try:
        stopwords = load_stopwords()
        if len(stopwords) > 0:
            log_test("TC-NLP-01", "停用词加载", "PASS", f"加载{len(stopwords)}个停用词")
        else:
            log_test("TC-NLP-01", "停用词加载", "WARN", "停用词文件为空或不存在")
    except Exception as e:
        log_test("TC-NLP-01", "停用词加载", "FAIL", str(e))
    
    # TC-NLP-02: 分词测试
    try:
        stopwords = load_stopwords()
        text = "这部电影真的很好看，剧情精彩"
        words = segment_words(text, stopwords)
        if len(words) > 0 and isinstance(words, list):
            log_test("TC-NLP-02", "分词测试", "PASS", f"分词结果: {words}")
        else:
            log_test("TC-NLP-02", "分词测试", "FAIL", "分词结果为空")
    except Exception as e:
        log_test("TC-NLP-02", "分词测试", "FAIL", str(e))
    
    # TC-NLP-03: 情感分析-正面（基于星级）
    try:
        result = compute_sentiment("这部电影真不错", 5)
        if result == "正面":
            log_test("TC-NLP-03", "情感分析-正面(星级)", "PASS", f"5星评论识别为'{result}'")
        else:
            log_test("TC-NLP-03", "情感分析-正面(星级)", "FAIL", f"期望'正面'，实际'{result}'")
    except Exception as e:
        log_test("TC-NLP-03", "情感分析-正面(星级)", "FAIL", str(e))
    
    # TC-NLP-04: 情感分析-负面（基于星级）
    try:
        result = compute_sentiment("太烂了", 1)
        if result == "负面":
            log_test("TC-NLP-04", "情感分析-负面(星级)", "PASS", f"1星评论识别为'{result}'")
        else:
            log_test("TC-NLP-04", "情感分析-负面(星级)", "FAIL", f"期望'负面'，实际'{result}'")
    except Exception as e:
        log_test("TC-NLP-04", "情感分析-负面(星级)", "FAIL", str(e))
    
    # TC-NLP-05: 情感分析-中性（基于星级）
    try:
        result = compute_sentiment("还行吧", 3)
        if result == "中性":
            log_test("TC-NLP-05", "情感分析-中性(星级)", "PASS", f"3星评论识别为'{result}'")
        else:
            log_test("TC-NLP-05", "情感分析-中性(星级)", "FAIL", f"期望'中性'，实际'{result}'")
    except Exception as e:
        log_test("TC-NLP-05", "情感分析-中性(星级)", "FAIL", str(e))
    
    # TC-NLP-06: 情感分析-短文本
    try:
        result = compute_sentiment("好", None)
        if result == "中性":
            log_test("TC-NLP-06", "情感分析-短文本", "PASS", "短文本(<5字符)识别为中性")
        else:
            log_test("TC-NLP-06", "情感分析-短文本", "FAIL", f"期望'中性'，实际'{result}'")
    except Exception as e:
        log_test("TC-NLP-06", "情感分析-短文本", "FAIL", str(e))
    
    # TC-NLP-07: 情感分析-无星级（使用SnowNLP）
    try:
        result = compute_sentiment("这部电影真的太棒了，强烈推荐！", None)
        if result in ["正面", "中性", "负面"]:
            log_test("TC-NLP-07", "情感分析-无星级", "PASS", f"SnowNLP识别为'{result}'")
        else:
            log_test("TC-NLP-07", "情感分析-无星级", "FAIL", f"结果异常: {result}")
    except Exception as e:
        log_test("TC-NLP-07", "情感分析-无星级", "FAIL", str(e))
    
    # TC-NLP-08: 词频统计测试
    try:
        df = pd.DataFrame({
            "comment_text": ["电影很好看", "剧情精彩", "演员演技好"]
        })
        word_freq = get_word_frequency(df, top_n=10)
        if len(word_freq) > 0 and isinstance(word_freq, list):
            log_test("TC-NLP-08", "词频统计", "PASS", f"统计到{len(word_freq)}个高频词")
        else:
            log_test("TC-NLP-08", "词频统计", "FAIL", "词频统计结果为空")
    except Exception as e:
        log_test("TC-NLP-08", "词频统计", "FAIL", str(e))
    
    # TC-NLP-09: 情感分布分析测试
    try:
        df = pd.DataFrame({
            "comment_text": ["很好看", "一般般", "太烂了", "不错不错", "还行"],
            "star_rating": [5, 3, 1, 4, 3]
        })
        dist = analyze_sentiment_distribution(df)
        if "正面" in dist and "中性" in dist and "负面" in dist:
            log_test("TC-NLP-09", "情感分布分析", "PASS", f"正面:{dist['正面']}, 中性:{dist['中性']}, 负面:{dist['负面']}")
        else:
            log_test("TC-NLP-09", "情感分布分析", "FAIL", "缺少情感类别")
    except Exception as e:
        log_test("TC-NLP-09", "情感分布分析", "FAIL", str(e))
    
    # TC-NLP-10: 平均情感得分测试
    try:
        df = pd.DataFrame({
            "comment_text": ["很好看", "不错", "还可以"]
        })
        score = compute_avg_sentiment_score(df)
        if 0 <= score <= 1:
            log_test("TC-NLP-10", "平均情感得分", "PASS", f"得分: {score:.3f}")
        else:
            log_test("TC-NLP-10", "平均情感得分", "FAIL", f"得分超出范围: {score}")
    except Exception as e:
        log_test("TC-NLP-10", "平均情感得分", "FAIL", str(e))
    
    # TC-NLP-11: 每日评论统计测试
    try:
        df = pd.DataFrame({
            "comment_time": ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-03"]
        })
        daily = get_daily_comment_count(df)
        if len(daily) == 3:
            log_test("TC-NLP-11", "每日评论统计", "PASS", f"统计到{len(daily)}天的数据")
        else:
            log_test("TC-NLP-11", "每日评论统计", "FAIL", f"期望3天，实际{len(daily)}天")
    except Exception as e:
        log_test("TC-NLP-11", "每日评论统计", "FAIL", str(e))
    
    # TC-NLP-12: 空DataFrame处理
    try:
        df = pd.DataFrame({"comment_text": []})
        score = compute_avg_sentiment_score(df)
        if score == 0.0:
            log_test("TC-NLP-12", "空DataFrame处理", "PASS", "正确返回0.0")
        else:
            log_test("TC-NLP-12", "空DataFrame处理", "FAIL", f"应返回0.0，实际{score}")
    except Exception as e:
        log_test("TC-NLP-12", "空DataFrame处理", "FAIL", str(e))
    
except Exception as e:
    log_test("TC-NLP-01", "NLP模块导入", "FAIL", str(e))

print()

# ============================================================================
# 第五部分：爬虫模块测试
# ============================================================================
print("=" * 80)
print("五、爬虫模块测试")
print("=" * 80)

try:
    from crawler.parser import parse_comments, parse_movie_info
    
    # TC-CR-01: 评论HTML解析测试
    try:
        test_html = '''
        <div class="comment-item">
            <div class="comment-info">
                <a>测试用户A</a>
                <span class="rating allstar50"></span>
                <span title="2024-01-01 12:00:00">时间</span>
            </div>
            <span class="short">这是一条测试评论，电影很好看！</span>
            <span class="votes">100</span>
        </div>
        <div class="comment-item">
            <div class="comment-info">
                <a>测试用户B</a>
                <span class="rating allstar20"></span>
                <span title="2024-01-02 13:00:00">时间</span>
            </div>
            <span class="short">不太好看</span>
            <span class="votes">50</span>
        </div>
        '''
        comments = parse_comments(test_html)
        if len(comments) == 2 and comments[0]["user_name"] == "测试用户A" and comments[0]["star_rating"] == 5:
            log_test("TC-CR-01", "评论HTML解析", "PASS", f"成功解析{len(comments)}条评论")
        else:
            log_test("TC-CR-01", "评论HTML解析", "FAIL", f"解析结果不正确: {comments}")
    except Exception as e:
        log_test("TC-CR-01", "评论HTML解析", "FAIL", str(e))
    
    # TC-CR-02: 电影信息解析测试
    try:
        test_html = '''
        <html>
        <span property="v:itemreviewed">测试电影名称</span>
        <span property="v:average">8.5</span>
        </html>
        '''
        movie_info = parse_movie_info(test_html)
        if movie_info and movie_info["movie_name"] == "测试电影名称" and movie_info["avg_rating"] == 8.5:
            log_test("TC-CR-02", "电影信息解析", "PASS", f"电影名: {movie_info['movie_name']}, 评分: {movie_info['avg_rating']}")
        else:
            log_test("TC-CR-02", "电影信息解析", "FAIL", f"解析结果: {movie_info}")
    except Exception as e:
        log_test("TC-CR-02", "电影信息解析", "FAIL", str(e))
    
    # TC-CR-03: 空HTML解析测试
    try:
        comments = parse_comments("")
        if comments == []:
            log_test("TC-CR-03", "空HTML解析", "PASS", "正确返回空列表")
        else:
            log_test("TC-CR-03", "空HTML解析", "FAIL", f"应返回空列表，实际: {comments}")
    except Exception as e:
        log_test("TC-CR-03", "空HTML解析", "FAIL", str(e))
    
    # TC-CR-04: 无评论项HTML解析
    try:
        test_html = '<html><body><div>没有评论</div></body></html>'
        comments = parse_comments(test_html)
        if comments == []:
            log_test("TC-CR-04", "无评论项HTML解析", "PASS", "正确返回空列表")
        else:
            log_test("TC-CR-04", "无评论项HTML解析", "FAIL", f"应返回空列表")
    except Exception as e:
        log_test("TC-CR-04", "无评论项HTML解析", "FAIL", str(e))
    
    # TC-CR-05: 无评分评论解析
    try:
        test_html = '''
        <div class="comment-item">
            <div class="comment-info">
                <a>用户无评分</a>
            </div>
            <span class="short">评论内容</span>
            <span class="votes">10</span>
        </div>
        '''
        comments = parse_comments(test_html)
        if len(comments) == 1 and comments[0]["star_rating"] is None:
            log_test("TC-CR-05", "无评分评论解析", "PASS", "正确处理无评分评论")
        else:
            log_test("TC-CR-05", "无评分评论解析", "FAIL", f"star_rating应为None")
    except Exception as e:
        log_test("TC-CR-05", "无评分评论解析", "FAIL", str(e))
    
    # TC-CR-06: 星级解析测试
    try:
        test_cases = [
            ('allstar10', 1),
            ('allstar20', 2),
            ('allstar30', 3),
            ('allstar40', 4),
            ('allstar50', 5)
        ]
        all_passed = True
        for class_name, expected in test_cases:
            test_html = f'''
            <div class="comment-item">
                <div class="comment-info"><a>用户</a></div>
                <span class="rating {class_name}"></span>
                <span class="short">评论</span>
            </div>
            '''
            comments = parse_comments(test_html)
            if not comments or comments[0]["star_rating"] != expected:
                all_passed = False
                break
        
        if all_passed:
            log_test("TC-CR-06", "星级解析", "PASS", "所有星级(1-5)解析正确")
        else:
            log_test("TC-CR-06", "星级解析", "FAIL", "星级解析有误")
    except Exception as e:
        log_test("TC-CR-06", "星级解析", "FAIL", str(e))
    
except Exception as e:
    log_test("TC-CR-01", "爬虫模块导入", "FAIL", str(e))

print()

# ============================================================================
# 第六部分：模块集成测试
# ============================================================================
print("=" * 80)
print("六、模块集成测试")
print("=" * 80)

# TC-INT-01: 数据库单例模式测试
try:
    from database.db_manager import get_db
    db1 = get_db()
    db2 = get_db()
    if db1 is db2:
        log_test("TC-INT-01", "数据库单例模式", "PASS", "get_db()返回同一实例")
    else:
        log_test("TC-INT-01", "数据库单例模式", "FAIL", "返回了不同实例")
except Exception as e:
    log_test("TC-INT-01", "数据库单例模式", "FAIL", str(e))

# TC-INT-02: 完整流程测试（解析->清洗->存储->分析）
try:
    # 1. 解析评论
    test_html = '''
    <div class="comment-item">
        <div class="comment-info">
            <a>集成测试用户</a>
            <span class="rating allstar50"></span>
            <span title="2024-01-01"></span>
        </div>
        <span class="short"><p>电影很好看！</p>https://test.com @某人 推荐！</span>
        <span class="votes">100</span>
    </div>
    '''
    comments = parse_comments(test_html)
    
    # 2. 清洗数据
    df = pd.DataFrame(comments)
    df['comment_text'] = df['comment_text'].apply(clean_text)
    
    # 3. 存储到数据库
    for comment in comments:
        comment['movie_id'] = 'integration_test'
    inserted = db.insert_comments(comments)
    
    # 4. 情感分析
    sentiment = compute_sentiment(df.iloc[0]['comment_text'], df.iloc[0]['star_rating'])
    
    if inserted > 0 and sentiment in ["正面", "中性", "负面"]:
        log_test("TC-INT-02", "完整流程测试", "PASS", f"解析->清洗->存储->分析流程正常，情感: {sentiment}")
    else:
        log_test("TC-INT-02", "完整流程测试", "FAIL", "流程中某环节失败")
except Exception as e:
    log_test("TC-INT-02", "完整流程测试", "FAIL", str(e))

print()

# ============================================================================
# 清理临时文件
# ============================================================================
try:
    os.close(temp_db_fd)
    os.unlink(temp_db_path)
except:
    pass

# ============================================================================
# 测试总结
# ============================================================================
print("=" * 80)
print("测试总结")
print("=" * 80)
print(f"通过: {len(test_results['passed'])} 个")
print(f"失败: {len(test_results['failed'])} 个")
print(f"警告: {len(test_results['warnings'])} 个")
print(f"总计: {len(test_results['passed']) + len(test_results['failed']) + len(test_results['warnings'])} 个")
print()

if test_results['failed']:
    print("失败的测试用例:")
    for result in test_results['failed']:
        print(f"  - [{result['test_id']}] {result['test_name']}: {result['message']}")
    print()

if test_results['warnings']:
    print("警告的测试用例:")
    for result in test_results['warnings']:
        print(f"  - [{result['test_id']}] {result['test_name']}: {result['message']}")
    print()

# 计算通过率
total = len(test_results['passed']) + len(test_results['failed'])
if total > 0:
    pass_rate = len(test_results['passed']) / total * 100
    print(f"通过率: {pass_rate:.1f}%")
else:
    print("通过率: N/A")

print()
print("=" * 80)
print("测试完成")
print("=" * 80)
