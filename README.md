# 豆瓣电影短评舆情分析平台

## 一、项目简介

本项目是一个基于 **Python + Streamlit** 的中文电影舆情分析 Web 应用。
用户通过输入电影名称（如“肖申克的救赎”）进行搜索并选择影片后，系统会抓取豆瓣电影短评、进行清洗与情感分析，并以可视化方式展示分析结果。

该项目针对课程作业中的“基于外部数据抓取解决实际问题”场景，实现了：

- 实时（按用户触发）获取电影评论数据
- 评论文本清洗与结构化存储
- 情感分类（正面/中性/负面）与加权指标
- 词频统计与词云展示
- 评论热度时间轴与同类电影对比

## 二、核心功能

1. 电影搜索
   - 输入电影名，调用豆瓣移动端搜索 API 获取匹配结果
   - 选择电影后自动带入电影 ID

2. 短评采集
   - 读取电影 ID 后抓取短评（默认 10 页，每页 20 条）
   - 采用移动端 API 与随机延时，降低反爬风险
   - 支持“刷新数据”后重新采集

3. 数据处理与存储
   - 评论文本清洗：去 HTML、去链接、去噪音字符、规范空白
   - 结果写入 SQLite，支持去重（按电影 ID + 用户名）

4. 情感分析与指标
   - 基于星级与文本内容做情感倾向判断
   - 计算正向/中性/负向占比
   - 提供加权好评率（融合星级、点赞数、情感强度）

5. 可视化
   - 情感分布饼图（支持加权视图）
   - 高频词词云（支持 AI 筛选与正则降级）
   - 评论时间轴（按日统计）
   - 评论列表按权重、点赞、时间可排序

## 三、技术栈

- Python 3.11+（示例在 3.x 下验证）
- Streamlit（Web 界面）
- requests（HTTP 抓取）
- BeautifulSoup + lxml（解析）
- SQLite（本地持久化）
- pandas（数据处理）
- jieba + SnowNLP（中文分词与情感分析）
- wordcloud + matplotlib（词云与绘图）
- pyecharts + streamlit-echarts（交互图表）

## 四、项目结构

```text
.
├─ app.py                     # Streamlit 主页面
├─ main.py                    # CLI 抓取入口（可选）
├─ requirements.txt
├─ config/
│  ├─ settings.py             # 抓取、模型、路径等配置
│  └─ headers.py              # 请求头与 Cookie 配置
├─ crawler/
│  ├─ douban_spider.py        # 豆瓣搜索/电影信息/评论抓取
│  └─ parser.py               # HTML/JSON 解析逻辑
├─ analysis/
│  ├─ data_cleaner.py         # 清洗逻辑
│  ├─ nlp_processor.py        # 情感分析、词频、排行与加权
│  └─ ai_client.py            # AI 关键词筛选客户端
├─ database/
│  └─ db_manager.py           # SQLite 管理
├─ tests/
│  └─ comprehensive_test.py   # 回归与功能测试
└─ docs/
   ├─ COOKIE配置说明.md
   ├─ 回归测试报告.md
   └─ 测试报告_二号测试员.md
```

## 五、安装与运行

### 1. 安装依赖

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 运行 Web 应用

```bash
streamlit run app.py
```

打开浏览器后即可访问本地页面。

### 3. 命令行抓取（可选）

```bash
python main.py --movie_id <电影ID> --max_pages 10
```

### 4. 环境变量（可选）

如需启用 AI 筛选词云或使用 Cookie，按以下方式配置：

```bash
export DEEPSEEK_API_KEY=你的API_KEY
export DOUBAN_COOKIE=你的Cookie（可选）
```

> 不要将真实 Key/Token/Cookie 提交到公开仓库。

## 六、数据来源与反爬说明

- 电影搜索 API：`m.douban.com/rexxar/api/v2/search/movie`
- 电影详情 API：`m.douban.com/rexxar/api/v2/movie/{id}`
- 评论 API：`m.douban.com/rexxar/api/v2/movie/{id}/interests`

目前策略：
- 使用移动端 API 替代网页抓取，降低页面反爬影响
- 固定 User-Agent 与 Referer
- 抓取时添加随机延迟（`REQUEST_DELAY_RANGE`）

## 七、测试

仓库内含测试脚本：

- `tests/comprehensive_test.py`
- `tests/test_modules.py`
- `tests/test_fixes.py`
- `tests/test_secondary.py`

## 八、部署

可将 Streamlit 应用部署到如下平台：

- Streamlit Community Cloud（推荐）
- Render / Railway（需按平台适配启动命令）

部署时请保证：
- `requirements.txt` 可用
- 配置必要环境变量（如 AI Key，可选）
- `database/sentiment.db` 可持久化到持久存储或重建策略

## 九、合规与风险提示

- 当前项目为学习演示用途，建议公开上线前补充 robots.txt 与访问边界说明。
- 抓取频率受控，但任何线上环境仍需添加速率上限与重试退避策略。
- 不得抓取或展示个人隐私敏感内容，已采用公开评论字段，未采集私密信息。

## 十、许可证与致谢

本项目以开源组件构建，遵循各依赖库许可。词云及图形展示仅用于课程与学习演示。
