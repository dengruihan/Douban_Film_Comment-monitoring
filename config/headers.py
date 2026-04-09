import random
import os

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
]

REFERER = "https://movie.douban.com/"

# ============================================================================
# Cookie配置说明
# ============================================================================
# 豆瓣需要登录Cookie才能获取完整评论数据
# 
# 获取方法：
# 1. 使用浏览器登录豆瓣网站
# 2. 打开开发者工具（F12或右键->检查）
# 3. 切换到Network（网络）标签
# 4. 刷新页面
# 5. 点击任意请求，在Headers（请求头）中找到Cookie字段
# 6. 复制完整的Cookie值
# 
# 配置方式（三选一）：
# 
# 方式1：环境变量（推荐，最安全）
#   export DOUBAN_COOKIE="你的Cookie内容"
#   或创建.env文件：DOUBAN_COOKIE="你的Cookie内容"
# 
# 方式2：直接修改此文件
#   将下面的空字符串替换为你的Cookie
#   COOKIE = "bid=xxxxx; dbcl2=xxxxx; ck=xxxxx; ..."
# 
# 方式3：不配置
#   未配置Cookie时只能获取前10页评论（约200条）
# 
# 注意事项：
# - Cookie包含敏感信息，请勿提交到Git仓库
# - Cookie会过期，需要定期更新
# - 建议使用环境变量方式配置
# ============================================================================

COOKIE = os.environ.get("DOUBAN_COOKIE", "")


def get_random_headers():
    """
    生成随机请求头
    
    Returns:
        dict: 包含User-Agent、Referer、Cookie的请求头字典
    """
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": REFERER,
        "Cookie": COOKIE,
    }
