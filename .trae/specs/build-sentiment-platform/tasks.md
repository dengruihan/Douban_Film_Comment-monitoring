# Tasks

- [x] Task 1: 创建项目目录结构与配置模块
  - [x] SubTask 1.1: 创建完整目录结构（config/, crawler/, database/, analysis/, assets/, logs/）
  - [x] SubTask 1.2: 编写 config/settings.py（全局配置项：MAX_PAGES, REQUEST_DELAY_RANGE, MAX_RETRIES, DB_PATH, 情感阈值等）
  - [x] SubTask 1.3: 编写 config/headers.py（User-Agent 池、Referer、Cookie 占位）
  - [x] SubTask 1.4: 编写 requirements.txt
  - [x] SubTask 1.5: 准备 assets/stopwords.txt（中文停用词表）

- [x] Task 2: 实现 SQLite 数据存储模块
  - [x] SubTask 2.1: 编写 database/db_manager.py（建表、插入、查询、去重逻辑）

- [x] Task 3: 实现爬虫模块
  - [x] SubTask 3.1: 编写 crawler/parser.py（HTML 解析：提取评论列表、电影基础信息）
  - [x] SubTask 3.2: 编写 crawler/douban_spider.py（请求逻辑、反爬策略、异常处理、重试机制、日志记录）

- [x] Task 4: 实现 NLP 分析模块
  - [x] SubTask 4.1: 编写 analysis/data_cleaner.py（正则清洗：去 HTML 标签、URL、@引用、Emoji、过滤短评论）
  - [x] SubTask 4.2: 编写 analysis/nlp_processor.py（jieba 分词、停用词过滤、词频统计、混合情感计算）

- [x] Task 5: 实现 Streamlit 可视化大屏
  - [x] SubTask 5.1: 编写 app.py（Streamlit 主程序：输入框、指标卡、饼图、词云、折线图、采集/分析流程串联）

- [x] Task 6: 实现爬虫独立执行入口
  - [x] SubTask 6.1: 编写 main.py（命令行参数解析、调用爬虫、输出进度）

# Task Dependencies
- [Task 2] depends on [Task 1]（需要配置模块中的 DB_PATH）
- [Task 3] depends on [Task 1]（需要配置模块中的 headers 和 settings）
- [Task 4] depends on [Task 1]（需要停用词表和配置）
- [Task 5] depends on [Task 2, Task 3, Task 4]（需要所有模块就绪）
- [Task 6] depends on [Task 2, Task 3]（需要爬虫和数据库模块）
