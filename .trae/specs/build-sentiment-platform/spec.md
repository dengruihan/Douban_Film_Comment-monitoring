# 基于豆瓣电影短评的舆情分析与可视化平台 Spec

## Why
公众对影视作品的态度呈现碎片化和情绪化特征，需要一个零代码门槛的 Web 应用，用户输入电影 ID 后即可一键生成该电影的舆情分析大屏（含情感倾向占比、高频词云、时间轴热度等）。

## What Changes
- 创建项目目录结构与配置模块（config/）
- 实现豆瓣短评爬虫核心逻辑（crawler/），含 Cookie 支持、反爬策略、异常处理
- 实现 SQLite 数据存储层（database/），含去重机制
- 实现 NLP 分析模块（analysis/），含数据清洗、jieba 分词、混合情感计算
- 实现 Streamlit Web 可视化大屏（app.py），含指标卡、饼图、词云、折线图
- 提供爬虫独立执行入口（main.py）

## Impact
- 新建完整项目，无已有代码受影响
- 依赖：requests, beautifulsoup4, pandas, jieba, snownlp, pyecharts, wordcloud, streamlit, lxml

## ADDED Requirements

### Requirement: 项目目录结构与配置
系统 SHALL 按照以下结构组织代码：
```
DoubanSentimentAnalysis/
├── app.py
├── main.py
├── requirements.txt
├── config/
│   ├── headers.py
│   └── settings.py
├── crawler/
│   ├── douban_spider.py
│   └── parser.py
├── database/
│   └── db_manager.py
├── analysis/
│   ├── nlp_processor.py
│   └── data_cleaner.py
└── assets/
    ├── stopwords.txt
    └── simhei.ttf
```

#### Scenario: 项目初始化
- **WHEN** 开发者克隆项目并安装依赖
- **THEN** 可通过 `pip install -r requirements.txt` 安装所有依赖，通过 `streamlit run app.py` 启动应用

### Requirement: 全局配置模块
系统 SHALL 在 `config/settings.py` 中提供以下可配置项：
- `MAX_PAGES`：单次采集最大页数，默认 10
- `REQUEST_DELAY_RANGE`：请求间隔范围，默认 (3, 6) 秒
- `MAX_RETRIES`：最大重试次数，默认 3
- `DB_PATH`：数据库文件路径
- `SENTIMENT_THRESHOLD_POS`：正面情感阈值，默认 0.6
- `SENTIMENT_THRESHOLD_NEG`：负面情感阈值，默认 0.4

系统 SHALL 在 `config/headers.py` 中提供：
- User-Agent 池（至少 5 个常见浏览器 UA）
- Referer 字段（豆瓣电影域名）
- Cookie 占位（用户可手动填入登录后的 Cookie）

#### Scenario: 配置加载
- **WHEN** 爬虫模块启动
- **THEN** 从 config 模块读取所有配置项，包括请求头、延时参数、重试策略

### Requirement: 豆瓣短评爬虫
系统 SHALL 能根据电影 ID 抓取豆瓣电影短评，提取以下字段：
- 用户名（user_name）
- 评分星级（star_rating，1-5，可能为空）
- 评论文本（comment_text）
- 有用数（vote_count）
- 评论时间（comment_time）

#### Scenario: 正常采集
- **WHEN** 用户输入有效的电影 ID（如 35267232）
- **THEN** 系统按页抓取短评，每页 20 条，最多采集 MAX_PAGES 页，每页请求间隔 3-6 秒随机延时

#### Scenario: 需要登录
- **WHEN** 请求返回 403 状态码
- **THEN** 系统记录警告日志，提示用户需要提供登录 Cookie，并停止采集

#### Scenario: 请求被限流
- **WHEN** 请求返回 418 状态码
- **THEN** 系统自动休眠 60 秒后重试，超过 MAX_RETRIES 次则跳过当前页

#### Scenario: 网络异常
- **WHEN** 发生 ConnectionError 或 Timeout
- **THEN** 系统记录错误日志，重试当前请求，超过 MAX_RETRIES 次则跳过

### Requirement: HTML 解析模块
系统 SHALL 从豆瓣短评页 HTML 中正确提取评论数据。

#### Scenario: 解析评论列表
- **WHEN** 接收到有效的短评页 HTML
- **THEN** 使用 BeautifulSoup4 解析，提取每条评论的用户名、星级、文本、有用数、时间，返回结构化列表

#### Scenario: 解析电影基础信息
- **WHEN** 接收到电影主页 HTML
- **THEN** 提取电影名称和平均评分

#### Scenario: 页面无评论
- **WHEN** 解析结果为空
- **THEN** 返回空列表，不抛出异常

### Requirement: SQLite 数据存储
系统 SHALL 使用 SQLite 存储数据，包含两张表：

**movie_info 表：**
- movie_id (TEXT, PK)
- movie_name (TEXT)
- avg_rating (REAL)

**movie_comments 表：**
- id (INTEGER, PK, AUTOINCREMENT)
- movie_id (TEXT, 索引)
- user_name (TEXT)
- star_rating (INTEGER)
- comment_text (TEXT)
- vote_count (INTEGER)
- comment_time (TEXT)

系统 SHALL 对 movie_comments 表设置 UNIQUE(movie_id, user_name) 约束，使用 INSERT OR IGNORE 防止重复数据。

#### Scenario: 写入评论数据
- **WHEN** 爬虫采集到一批评论
- **THEN** 批量写入数据库，重复数据自动跳过

#### Scenario: 查询电影评论
- **WHEN** 分析模块请求数据
- **THEN** 返回指定 movie_id 的所有评论，按评论时间排序

### Requirement: 数据清洗模块
系统 SHALL 对原始评论文本进行清洗：
- 去除 HTML 标签
- 去除换行符和多余空白
- 去除 @用户 引用
- 去除 URL 链接
- 去除 Emoji 和特殊字符（保留中文标点）
- 过滤空评论和过短评论（< 2 字）

#### Scenario: 清洗含噪声文本
- **WHEN** 输入 "<p>这电影真不错！</p>@某人 推荐看 https://xxx"
- **THEN** 输出 "这电影真不错！推荐看"

### Requirement: NLP 情感分析模块
系统 SHALL 采用"豆瓣星级 + SnowNLP"混合策略进行情感分类：

- **强负面规则**：star_rating 为 1 或 2 → 负面
- **强正面规则**：star_rating 为 5 → 正面
- **模糊区间**：star_rating 为 3 或 4 时，调用 SnowNLP：
  - sentiments > 0.6 → 正面
  - sentiments < 0.4 → 负面
  - 其余 → 中性
- **无星级**：仅依赖 SnowNLP，阈值同上
- **过短评论**（< 5 字）：默认中性

系统 SHALL 使用 jieba 精确模式分词，加载停用词表过滤无意义词，统计 Top 100 高频词。

#### Scenario: 5 星评论
- **WHEN** star_rating = 5，评论文本为 "太好看了"
- **THEN** 情感分类为"正面"

#### Scenario: 3 星评论
- **WHEN** star_rating = 3，SnowNLP sentiments = 0.7
- **THEN** 情感分类为"正面"

#### Scenario: 无星级短评论
- **WHEN** star_rating 为空，评论长度 < 5 字
- **THEN** 情感分类为"中性"

### Requirement: Streamlit 可视化大屏
系统 SHALL 提供 Streamlit Web 应用，包含以下可视化组件：

1. **顶部指标卡**：采集评论总数、综合好评率、平均情感得分
2. **左上区域**：环形饼图展示正面/中性/负面评论占比（Pyecharts）
3. **右上区域**：词云图，字体大小代表词频（WordCloud，第一版单色，指定中文字体 simhei.ttf）
4. **底部区域**：折线图展示每日评论量时间轴（Pyecharts）

#### Scenario: 用户输入电影 ID
- **WHEN** 用户在输入框输入电影 ID 并点击"开始分析"
- **THEN** 系统先检查数据库是否已有该电影数据，若无则启动爬虫采集，采集完成后展示分析大屏

#### Scenario: 数据已存在
- **WHEN** 数据库已有该电影的评论数据
- **THEN** 直接从数据库读取并展示分析结果，不重复采集

#### Scenario: 采集失败
- **WHEN** 爬虫因网络问题无法获取数据
- **THEN** 页面显示错误提示"当前网络请求受限，请稍后再试"

### Requirement: 爬虫独立执行入口
系统 SHALL 提供 main.py 作为爬虫独立运行入口，支持命令行参数指定电影 ID。

#### Scenario: 命令行运行爬虫
- **WHEN** 执行 `python main.py --movie_id 35267232`
- **THEN** 爬虫开始采集数据并写入数据库，控制台输出采集进度

### Requirement: 日志记录
系统 SHALL 使用 Python logging 模块记录运行日志，包括：
- 请求成功/失败信息
- 重试信息
- 数据写入统计
- 异常堆栈

日志输出到控制台和 `logs/crawler.log` 文件。

#### Scenario: 爬虫运行日志
- **WHEN** 爬虫执行过程中发生异常
- **THEN** 异常信息被记录到日志文件，不影响其他页面的采集
