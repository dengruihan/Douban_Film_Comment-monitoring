# Cookie 配置说明（备选方案）

当前系统使用移动端API，**无需Cookie**即可正常工作。

但如果遇到以下情况，可以配置Cookie作为备选：
- 移动端API被限制
- 需要获取更多评论数据
- 需要访问需要登录的内容

## 获取Cookie的方法

1. 使用浏览器登录豆瓣网站 (https://www.douban.com)
2. 打开开发者工具（F12 或 右键→检查）
3. 切换到 **Network（网络）** 标签
4. 刷新页面
5. 点击任意请求，在 **Headers（请求头）** 中找到 `Cookie` 字段
6. 复制完整的Cookie值（通常很长，包含 bid、dbcl2、ck 等）

## 配置方式

### 方式1：环境变量（推荐，最安全）

```bash
# macOS/Linux
export DOUBAN_COOKIE="你的Cookie内容"

# 或者创建 .env 文件
echo 'DOUBAN_COOKIE="你的Cookie内容"' > .env
```

### 方式2：直接修改配置文件

编辑 `config/headers.py` 文件，找到这一行：

```python
COOKIE = os.environ.get("DOUBAN_COOKIE", "")
```

改为：

```python
COOKIE = "你的Cookie内容"
```

## 注意事项

⚠️ **安全提醒**：
- Cookie包含敏感信息，请勿分享或提交到Git仓库
- Cookie会过期（通常几周到几个月），需要定期更新
- 建议使用环境变量方式，避免泄露

## 验证Cookie是否生效

运行测试脚本：

```bash
source venv/bin/activate
python -c "from config.headers import COOKIE; print('Cookie已配置' if COOKIE else '未配置Cookie')"
```

## 当前状态

✅ 系统已使用移动端API，无需Cookie即可正常工作
📝 Cookie配置仅作为备选方案，通常不需要配置
