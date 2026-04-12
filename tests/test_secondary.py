#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
豆瓣电影短评舆情分析平台 - 二号测试员独立测试
测试员: 产品测试员二号
测试日期: 2026-04-09
测试类型: 二次验证 + 额外独立测试
"""

import sys
import os
import sqlite3
import tempfile
import pandas as pd

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
        print(f"✓ [{test_id}] {test_name} - 通过: {message}")
    elif status == "FAIL":
        test_results["failed"].append(result)
        print(f"✗ [{test_id}] {test_name} - 失败: {message}")
    else:
        test_results["warnings"].append(result)
        print(f"⚠ [{test_id}] {test_name} - 警告: {message}")

print("=" * 80)
print("豆瓣电影短评舆情分析平台 - 二号测试员独立测试报告")
print("=" * 80)
print()

# ============================================================================
# 第一部分: 复现一号测试员的修复验证测试
# ============================================================================
print("=" * 80)
print("一、复现一号测试员修复验证 - NLP情感分析逻辑")
print("=" * 80)

try:
    from analysis.nlp_processor import compute_sentiment
    
    # TC-SEC-NLP-01: 短评论"烂片"+1星 → 负面
    result = compute_sentiment("烂片", 1)
    if result == "负面":
        log_test("TC-SEC-NLP-01", "短评论'烂片'+1星", "PASS", f"正确识别为'{result}'")
    else:
        log_test("TC-SEC-NLP-01", "短评论'烂片'+1星", "FAIL", f"期望'负面',实际'{result}'")
    
    # TC-SEC-NLP-02: 短评论"神作"+5星 → 正面
    result = compute_sentiment("神作", 5)
    if result == "正面":
        log_test("TC-SEC-NLP-02", "短评论'神作'+5星", "PASS", f"正确识别为'{result}'")
    else:
        log_test("TC-SEC-NLP-02", "短评论'神作'+5星", "FAIL", f"期望'正面',实际'{result}'")
    
    # TC-SEC-NLP-03: 短评论"还行"+3星 → 中性
    result = compute_sentiment("还行", 3)
    if result == "中性":
        log_test("TC-SEC-NLP-03", "短评论'还行'+3星", "PASS", f"正确识别为'{result}'")
    else:
        log_test("TC-SEC-NLP-03", "短评论'还行'+3星", "FAIL", f"期望'中性',实际'{result}'")
    
    # TC-SEC-NLP-04: 星级优先级验证
    result1 = compute_sentiment("好", 1)  # 正面词+1星应识别为负面
    result2 = compute_sentiment("烂", 5)  # 负面词+5星应识别为正面
    if result1 == "负面" and result2 == "正面":
        log_test("TC-SEC-NLP-04", "星级评分优先级", "PASS", f"1星'好'→'{result1}', 5星'烂'→'{result2}'")
    else:
        log_test("TC-SEC-NLP-04", "星级评分优先级", "FAIL", f"优先级错误: 1星'好'→'{result1}', 5星'烂'→'{result2}'")
    
except Exception as e:
    log_test("TC-SEC-NLP-01", "NLP模块导入", "FAIL", str(e))

print()

# ============================================================================
# 第二部分: 字体功能独立验证（不导入app.py）
# ============================================================================
print("=" * 80)
print("二、字体功能独立验证")
print("=" * 80)

try:
    import platform
    
    # TC-SEC-FONT-01: 直接验证字体文件存在性
    system = platform.system()
    print(f"当前系统: {system}")
    
    if system == "Darwin":  # macOS
        system_fonts = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc"
        ]
        
        found_fonts = []
        for font in system_fonts:
            if os.path.exists(font):
                found_fonts.append(font)
        
        if found_fonts:
            log_test("TC-SEC-FONT-01", "macOS系统字体查找", "PASS", f"找到{len(found_fonts)}个字体: {found_fonts[0]}")
        else:
            log_test("TC-SEC-FONT-01", "macOS系统字体查找", "FAIL", "未找到任何中文字体")
    else:
        log_test("TC-SEC-FONT-01", "系统字体查找", "WARN", f"当前系统{system}，跳过macOS测试")
    
    # TC-SEC-FONT-02: 验证字体查找函数代码逻辑
    with open("/Users/radmonkt/Documents/学术/高二/高二下/应用编程/舆情分析/app.py", 'r', encoding='utf-8') as f:
        content = f.read()
        
        checks = {
            "函数定义": 'def get_chinese_font_path()' in content,
            "macOS支持": '"Darwin"' in content or "'Darwin'" in content,
            "Windows支持": '"Windows"' in content or "'Windows'" in content,
            "Linux支持": '"Linux"' in content or "'Linux'" in content,
            "项目字体优先": 'FONT_PATH' in content and '优先使用项目字体' in content,
        }
        
        all_passed = all(checks.values())
        if all_passed:
            log_test("TC-SEC-FONT-02", "字体查找函数逻辑", "PASS", "函数定义完整，支持跨平台")
        else:
            missing = [k for k, v in checks.items() if not v]
            log_test("TC-SEC-FONT-02", "字体查找函数逻辑", "FAIL", f"缺少: {', '.join(missing)}")
    
except Exception as e:
    log_test("TC-SEC-FONT-01", "字体功能验证", "FAIL", str(e))

print()

# ============================================================================
# 第三部分: Cookie配置独立验证
# ============================================================================
print("=" * 80)
print("三、Cookie配置独立验证")
print("=" * 80)

try:
    from config.headers import COOKIE, get_random_headers
    
    # TC-SEC-COOKIE-01: 配置说明完整性
    with open("/Users/radmonkt/Documents/学术/高二/高二下/应用编程/舆情分析/config/headers.py", 'r', encoding='utf-8') as f:
        content = f.read()
        
        checks = {
            "获取方法说明": "获取方法" in content or "获取Cookie" in content,
            "环境变量支持": "DOUBAN_COOKIE" in content,
            "注意事项": "注意事项" in content or "敏感信息" in content,
        }
        
        all_passed = all(checks.values())
        if all_passed:
            log_test("TC-SEC-COOKIE-01", "配置说明完整性", "PASS", "包含获取方法、环境变量支持、注意事项")
        else:
            missing = [k for k, v in checks.items() if not v]
            log_test("TC-SEC-COOKIE-01", "配置说明完整性", "FAIL", f"缺少: {', '.join(missing)}")
    
    # TC-SEC-COOKIE-02: Headers包含Cookie字段
    headers = get_random_headers()
    if "Cookie" in headers:
        log_test("TC-SEC-COOKIE-02", "Headers包含Cookie", "PASS", "get_random_headers()返回包含Cookie字段")
    else:
        log_test("TC-SEC-COOKIE-02", "Headers包含Cookie", "FAIL", "headers缺少Cookie字段")
    
except Exception as e:
    log_test("TC-SEC-COOKIE-01", "Cookie模块导入", "FAIL", str(e))

print()

# ============================================================================
# 第四部分: 边界条件测试
# ============================================================================
print("=" * 80)
print("四、边界条件测试")
print("=" * 80)

try:
    from analysis.nlp_processor import compute_sentiment
    
    # TC-SEC-EDGE-01: 空文本测试
    result = compute_sentiment("", 1)
    if result == "负面":
        log_test("TC-SEC-EDGE-01", "空文本+1星", "PASS", f"正确识别为'{result}'")
    else:
        log_test("TC-SEC-EDGE-01", "空文本+1星", "FAIL", f"期望'负面',实际'{result}'")
    
    # TC-SEC-EDGE-02: 空文本+无星级
    result = compute_sentiment("", None)
    if result == "中性":
        log_test("TC-SEC-EDGE-02", "空文本+无星级", "PASS", f"正确识别为'{result}'")
    else:
        log_test("TC-SEC-EDGE-02", "空文本+无星级", "FAIL", f"期望'中性',实际'{result}'")
    
    # TC-SEC-EDGE-03: 单字符测试
    result = compute_sentiment("a", 5)
    if result == "正面":
        log_test("TC-SEC-EDGE-03", "单字符+5星", "PASS", f"正确识别为'{result}'")
    else:
        log_test("TC-SEC-EDGE-03", "单字符+5星", "FAIL", f"期望'正面',实际'{result}'")
    
    # TC-SEC-EDGE-04: 正面词+低星级（星级优先）
    result = compute_sentiment("好", 2)
    if result == "负面":
        log_test("TC-SEC-EDGE-04", "正面词'好'+2星", "PASS", f"星级优先，识别为'{result}'")
    else:
        log_test("TC-SEC-EDGE-04", "正面词'好'+2星", "FAIL", f"期望'负面'(星级优先),实际'{result}'")
    
    # TC-SEC-EDGE-05: 长文本测试
    long_text = "这是一条非常非常非常非常非常长的评论内容测试文本"
    result = compute_sentiment(long_text, 1)
    if result == "负面":
        log_test("TC-SEC-EDGE-05", "长文本+1星", "PASS", f"正确识别为'{result}'")
    else:
        log_test("TC-SEC-EDGE-05", "长文本+1星", "FAIL", f"期望'负面',实际'{result}'")
    
    # TC-SEC-EDGE-06: 特殊字符测试
    result = compute_sentiment("★★★★★", 3)
    if result == "中性":
        log_test("TC-SEC-EDGE-06", "特殊字符+3星", "PASS", f"正确识别为'{result}'")
    else:
        log_test("TC-SEC-EDGE-06", "特殊字符+3星", "FAIL", f"期望'中性',实际'{result}'")
    
except Exception as e:
    log_test("TC-SEC-EDGE-01", "边界条件测试", "FAIL", str(e))

print()

# ============================================================================
# 第五部分: 异常场景测试
# ============================================================================
print("=" * 80)
print("五、异常场景测试")
print("=" * 80)

try:
    from analysis.data_cleaner import clean_text, clean_dataframe
    from analysis.nlp_processor import compute_sentiment, compute_avg_sentiment_score
    
    # TC-SEC-EX-01: None值清洗测试
    try:
        result = clean_text(None)
        log_test("TC-SEC-EX-01", "None值清洗", "WARN", f"返回: {result} (应考虑异常处理)")
    except Exception as e:
        log_test("TC-SEC-EX-01", "None值清洗", "PASS", f"正确抛出异常: {type(e).__name__}")
    
    # TC-SEC-EX-02: 空DataFrame情感得分
    df = pd.DataFrame({"comment_text": []})
    score = compute_avg_sentiment_score(df)
    if score == 0.0:
        log_test("TC-SEC-EX-02", "空DataFrame情感得分", "PASS", f"正确返回0.0")
    else:
        log_test("TC-SEC-EX-02", "空DataFrame情感得分", "FAIL", f"期望0.0,实际{score}")
    
    # TC-SEC-EX-03: 无星级None值测试
    result = compute_sentiment("测试文本", None)
    if result in ["正面", "中性", "负面"]:
        log_test("TC-SEC-EX-03", "无星级(None)测试", "PASS", f"正确处理，返回'{result}'")
    else:
        log_test("TC-SEC-EX-03", "无星级(None)测试", "FAIL", f"返回值异常: {result}")
    
    # TC-SEC-EX-04: 超长文本测试
    super_long = "测试" * 10000
    result = compute_sentiment(super_long, 3)
    if result in ["正面", "中性", "负面"]:
        log_test("TC-SEC-EX-04", "超长文本测试", "PASS", f"正确处理超长文本，返回'{result}'")
    else:
        log_test("TC-SEC-EX-04", "超长文本测试", "FAIL", f"返回值异常: {result}")
    
except Exception as e:
    log_test("TC-SEC-EX-01", "异常场景测试", "FAIL", str(e))

print()

# ============================================================================
# 第六部分: 数据库压力测试
# ============================================================================
print("=" * 80)
print("六、数据库压力测试")
print("=" * 80)

temp_db_fd, temp_db_path = tempfile.mkstemp(suffix='.db')

try:
    from database.db_manager import DatabaseManager
    
    db = DatabaseManager(temp_db_path)
    
    # TC-SEC-PERF-01: 大量评论插入测试
    large_comments = []
    for i in range(1000):
        large_comments.append({
            "movie_id": "perf_test",
            "user_name": f"用户{i}",
            "star_rating": (i % 5) + 1,
            "comment_text": f"这是第{i}条测试评论内容",
            "vote_count": i,
            "comment_time": "2024-01-01"
        })
    
    inserted = db.insert_comments(large_comments)
    if inserted == 1000:
        log_test("TC-SEC-PERF-01", "批量插入1000条评论", "PASS", f"成功插入{inserted}条")
    else:
        log_test("TC-SEC-PERF-01", "批量插入1000条评论", "FAIL", f"期望1000条,实际{inserted}条")
    
    # TC-SEC-PERF-02: 大量评论查询测试
    comments = db.get_comments("perf_test")
    if len(comments) == 1000:
        log_test("TC-SEC-PERF-02", "查询1000条评论", "PASS", f"成功查询{len(comments)}条")
    else:
        log_test("TC-SEC-PERF-02", "查询1000条评论", "FAIL", f"期望1000条,实际{len(comments)}条")
    
    # TC-SEC-PERF-03: 评论计数测试
    count = db.comment_count("perf_test")
    if count == 1000:
        log_test("TC-SEC-PERF-03", "评论计数", "PASS", f"正确计数{count}条")
    else:
        log_test("TC-SEC-PERF-03", "评论计数", "FAIL", f"期望1000,实际{count}")
    
except Exception as e:
    log_test("TC-SEC-PERF-01", "数据库压力测试", "FAIL", str(e))

finally:
    try:
        os.close(temp_db_fd)
        os.unlink(temp_db_path)
    except:
        pass

print()

# ============================================================================
# 第七部分: 数据清洗深度测试
# ============================================================================
print("=" * 80)
print("七、数据清洗深度测试")
print("=" * 80)

try:
    from analysis.data_cleaner import clean_text
    
    # TC-SEC-DC-01: 多层嵌套HTML
    text = "<div><p><span>测试</span></p></div>"
    cleaned = clean_text(text)
    if "<div>" not in cleaned and "<p>" not in cleaned:
        log_test("TC-SEC-DC-01", "多层嵌套HTML清洗", "PASS", f"'{text}' -> '{cleaned}'")
    else:
        log_test("TC-SEC-DC-01", "多层嵌套HTML清洗", "FAIL", f"未完全清洗: '{cleaned}'")
    
    # TC-SEC-DC-02: 多个URL清洗
    text = "链接1 http://a.com 链接2 https://b.com 链接3 www.c.com"
    cleaned = clean_text(text)
    if "http://" not in cleaned and "https://" not in cleaned:
        log_test("TC-SEC-DC-02", "多个URL清洗", "PASS", "所有URL已移除")
    else:
        log_test("TC-SEC-DC-02", "多个URL清洗", "FAIL", f"URL未完全清洗: '{cleaned}'")
    
    # TC-SEC-DC-03: 混合特殊字符
    text = "评论【推荐】★★★☆☆<br/>测试"
    cleaned = clean_text(text)
    if "<br/>" not in cleaned:
        log_test("TC-SEC-DC-03", "混合特殊字符清洗", "PASS", f"'{text}' -> '{cleaned}'")
    else:
        log_test("TC-SEC-DC-03", "混合特殊字符清洗", "FAIL", f"未完全清洗: '{cleaned}'")
    
    # TC-SEC-DC-04: Unicode特殊字符
    text = "测试\u0000\u0001\u0002内容"
    cleaned = clean_text(text)
    if "\u0000" not in cleaned:
        log_test("TC-SEC-DC-04", "Unicode特殊字符清洗", "PASS", "控制字符已移除")
    else:
        log_test("TC-SEC-DC-04", "Unicode特殊字符清洗", "FAIL", f"控制字符未移除: '{cleaned}'")
    
except Exception as e:
    log_test("TC-SEC-DC-01", "数据清洗深度测试", "FAIL", str(e))

print()

# ============================================================================
# 测试总结
# ============================================================================
print("=" * 80)
print("二号测试员独立测试总结")
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
print("二号测试员独立测试完成")
print("=" * 80)

# 返回测试结果
if __name__ == "__main__":
    import json
    print("\n测试结果JSON:")
    print(json.dumps(test_results, ensure_ascii=False, indent=2))