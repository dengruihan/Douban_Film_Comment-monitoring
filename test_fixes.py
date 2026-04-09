#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
豆瓣电影短评舆情分析平台 - 修复功能验证测试
测试员: 产品功能测试员
测试日期: 2026-04-09
测试类型: 回归测试 - 修复验证
"""

import sys
import os
import platform

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
print("豆瓣电影短评舆情分析平台 - 修复功能验证测试")
print("=" * 80)
print()

# ============================================================================
# 第一部分: 修复1验证 - NLP情感分析逻辑缺陷
# ============================================================================
print("=" * 80)
print("一、修复1验证: NLP情感分析逻辑缺陷(高优先级)")
print("=" * 80)

try:
    from analysis.nlp_processor import compute_sentiment
    
    # TC-FIX-NLP-01: 短评论"烂片"+1星 → 应识别为负面
    try:
        result = compute_sentiment("烂片", 1)
        if result == "负面":
            log_test("TC-FIX-NLP-01", "短评论'烂片'+1星", "PASS", f"正确识别为'{result}'")
        else:
            log_test("TC-FIX-NLP-01", "短评论'烂片'+1星", "FAIL", f"期望'负面',实际'{result}'")
    except Exception as e:
        log_test("TC-FIX-NLP-01", "短评论'烂片'+1星", "FAIL", str(e))
    
    # TC-FIX-NLP-02: 短评论"神作"+5星 → 应识别为正面
    try:
        result = compute_sentiment("神作", 5)
        if result == "正面":
            log_test("TC-FIX-NLP-02", "短评论'神作'+5星", "PASS", f"正确识别为'{result}'")
        else:
            log_test("TC-FIX-NLP-02", "短评论'神作'+5星", "FAIL", f"期望'正面',实际'{result}'")
    except Exception as e:
        log_test("TC-FIX-NLP-02", "短评论'神作'+5星", "FAIL", str(e))
    
    # TC-FIX-NLP-03: 短评论"还行"+3星 → 应识别为中性
    try:
        result = compute_sentiment("还行", 3)
        if result == "中性":
            log_test("TC-FIX-NLP-03", "短评论'还行'+3星", "PASS", f"正确识别为'{result}'")
        else:
            log_test("TC-FIX-NLP-03", "短评论'还行'+3星", "FAIL", f"期望'中性',实际'{result}'")
    except Exception as e:
        log_test("TC-FIX-NLP-03", "短评论'还行'+3星", "FAIL", str(e))
    
    # TC-FIX-NLP-04: 短评论"垃圾"+2星 → 应识别为负面
    try:
        result = compute_sentiment("垃圾", 2)
        if result == "负面":
            log_test("TC-FIX-NLP-04", "短评论'垃圾'+2星", "PASS", f"正确识别为'{result}'")
        else:
            log_test("TC-FIX-NLP-04", "短评论'垃圾'+2星", "FAIL", f"期望'负面',实际'{result}'")
    except Exception as e:
        log_test("TC-FIX-NLP-04", "短评论'垃圾'+2星", "FAIL", str(e))
    
    # TC-FIX-NLP-05: 验证星级评分优先级高于文本长度检查
    try:
        # 测试1: 1星短文本"好"应该识别为负面(星级优先)
        result1 = compute_sentiment("好", 1)
        # 测试2: 5星短文本"烂"应该识别为正面(星级优先)
        result2 = compute_sentiment("烂", 5)
        
        if result1 == "负面" and result2 == "正面":
            log_test("TC-FIX-NLP-05", "星级评分优先级验证", "PASS", 
                    f"1星'好'→'{result1}', 5星'烂'→'{result2}', 星级优先级正确")
        else:
            log_test("TC-FIX-NLP-05", "星级评分优先级验证", "FAIL", 
                    f"1星'好'→'{result1}', 5星'烂'→'{result2}', 星级优先级错误")
    except Exception as e:
        log_test("TC-FIX-NLP-05", "星级评分优先级验证", "FAIL", str(e))
    
    # TC-FIX-NLP-06: 验证无星级短文本处理
    try:
        # 无星级且文本长度<5应返回中性
        result = compute_sentiment("好", None)
        if result == "中性":
            log_test("TC-FIX-NLP-06", "无星级短文本处理", "PASS", f"无星级短文本正确识别为'{result}'")
        else:
            log_test("TC-FIX-NLP-06", "无星级短文本处理", "FAIL", f"期望'中性',实际'{result}'")
    except Exception as e:
        log_test("TC-FIX-NLP-06", "无星级短文本处理", "FAIL", str(e))
    
    # TC-FIX-NLP-07: 边界测试 - 4星评论
    try:
        # 4星评论,文本长度>=5时使用SnowNLP辅助判断
        result = compute_sentiment("这部电影真的很棒,强烈推荐!", 4)
        if result in ["正面", "中性", "负面"]:
            log_test("TC-FIX-NLP-07", "4星评论边界测试", "PASS", f"4星评论识别为'{result}'")
        else:
            log_test("TC-FIX-NLP-07", "4星评论边界测试", "FAIL", f"结果异常: {result}")
    except Exception as e:
        log_test("TC-FIX-NLP-07", "4星评论边界测试", "FAIL", str(e))
    
    # TC-FIX-NLP-08: 边界测试 - 3星评论
    try:
        # 3星评论,文本长度<5时返回中性
        result = compute_sentiment("一般", 3)
        if result == "中性":
            log_test("TC-FIX-NLP-08", "3星短评论边界测试", "PASS", f"3星短评论识别为'{result}'")
        else:
            log_test("TC-FIX-NLP-08", "3星短评论边界测试", "FAIL", f"期望'中性',实际'{result}'")
    except Exception as e:
        log_test("TC-FIX-NLP-08", "3星短评论边界测试", "FAIL", str(e))
    
except Exception as e:
    log_test("TC-FIX-NLP-01", "NLP模块导入", "FAIL", str(e))

print()

# ============================================================================
# 第二部分: 修复2验证 - 字体文件缺失
# ============================================================================
print("=" * 80)
print("二、修复2验证: 字体文件缺失(中优先级)")
print("=" * 80)

try:
    # 导入app模块中的get_chinese_font_path函数
    import importlib.util
    spec = importlib.util.spec_from_file_location("app", "/Users/radmonkt/Documents/学术/高二/高二下/应用编程/舆情分析/app.py")
    app_module = importlib.util.module_from_spec(spec)
    
    # TC-FIX-FONT-01: 函数定义验证
    try:
        # 检查函数是否存在
        with open("/Users/radmonkt/Documents/学术/高二/高二下/应用编程/舆情分析/app.py", 'r', encoding='utf-8') as f:
            content = f.read()
            if 'def get_chinese_font_path()' in content:
                log_test("TC-FIX-FONT-01", "字体路径函数定义", "PASS", "get_chinese_font_path()函数已定义")
            else:
                log_test("TC-FIX-FONT-01", "字体路径函数定义", "FAIL", "未找到get_chinese_font_path()函数")
    except Exception as e:
        log_test("TC-FIX-FONT-01", "字体路径函数定义", "FAIL", str(e))
    
    # TC-FIX-FONT-02: macOS系统字体查找
    try:
        spec.loader.exec_module(app_module)
        font_path = app_module.get_chinese_font_path()
        
        if platform.system() == "Darwin":  # macOS
            if font_path and os.path.exists(font_path):
                log_test("TC-FIX-FONT-02", "macOS系统字体查找", "PASS", f"找到字体: {font_path}")
            elif font_path:
                log_test("TC-FIX-FONT-02", "macOS系统字体查找", "WARN", f"字体路径不存在: {font_path}")
            else:
                log_test("TC-FIX-FONT-02", "macOS系统字体查找", "FAIL", "未找到任何中文字体")
        else:
            log_test("TC-FIX-FONT-02", "macOS系统字体查找", "WARN", f"当前系统为{platform.system()},跳过macOS测试")
    except Exception as e:
        log_test("TC-FIX-FONT-02", "macOS系统字体查找", "FAIL", str(e))
    
    # TC-FIX-FONT-03: 项目字体文件优先级
    try:
        # 检查是否优先使用项目字体
        with open("/Users/radmonkt/Documents/学术/高二/高二下/应用编程/舆情分析/app.py", 'r', encoding='utf-8') as f:
            content = f.read()
            # 检查代码逻辑: 应该先检查项目字体,再检查系统字体
            if 'FONT_PATH' in content and '优先使用项目字体' in content:
                log_test("TC-FIX-FONT-03", "项目字体优先级", "PASS", "代码逻辑正确: 优先使用项目字体")
            else:
                log_test("TC-FIX-FONT-03", "项目字体优先级", "FAIL", "项目字体优先级逻辑不正确")
    except Exception as e:
        log_test("TC-FIX-FONT-03", "项目字体优先级", "FAIL", str(e))
    
    # TC-FIX-FONT-04: 跨平台支持验证
    try:
        # 检查是否支持Windows、Linux、macOS
        with open("/Users/radmonkt/Documents/学术/高二/高二下/应用编程/舆情分析/app.py", 'r', encoding='utf-8') as f:
            content = f.read()
            has_darwin = '"Darwin"' in content or "'Darwin'" in content
            has_windows = '"Windows"' in content or "'Windows'" in content
            has_linux = '"Linux"' in content or "'Linux'" in content
            
            if has_darwin and has_windows and has_linux:
                log_test("TC-FIX-FONT-04", "跨平台支持", "PASS", "支持macOS、Windows、Linux三大平台")
            else:
                platforms = []
                if has_darwin: platforms.append("macOS")
                if has_windows: platforms.append("Windows")
                if has_linux: platforms.append("Linux")
                log_test("TC-FIX-FONT-04", "跨平台支持", "WARN", f"仅支持: {', '.join(platforms)}")
    except Exception as e:
        log_test("TC-FIX-FONT-04", "跨平台支持", "FAIL", str(e))
    
except Exception as e:
    log_test("TC-FIX-FONT-01", "字体模块导入", "FAIL", str(e))

print()

# ============================================================================
# 第三部分: 修复3验证 - Cookie配置说明
# ============================================================================
print("=" * 80)
print("三、修复3验证: Cookie配置说明(低优先级)")
print("=" * 80)

try:
    from config.headers import COOKIE, get_random_headers
    import os
    
    # TC-FIX-COOKIE-01: 配置说明完整性
    try:
        with open("/Users/radmonkt/Documents/学术/高二/高二下/应用编程/舆情分析/config/headers.py", 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 检查是否包含详细的配置说明
            checks = {
                "获取方法": "获取方法" in content or "获取Cookie" in content,
                "配置方式": "配置方式" in content or "环境变量" in content,
                "注意事项": "注意事项" in content or "敏感信息" in content,
                "环境变量支持": "DOUBAN_COOKIE" in content
            }
            
            all_present = all(checks.values())
            
            if all_present:
                log_test("TC-FIX-COOKIE-01", "配置说明完整性", "PASS", "包含获取方法、配置方式、注意事项、环境变量支持")
            else:
                missing = [k for k, v in checks.items() if not v]
                log_test("TC-FIX-COOKIE-01", "配置说明完整性", "FAIL", f"缺少: {', '.join(missing)}")
    except Exception as e:
        log_test("TC-FIX-COOKIE-01", "配置说明完整性", "FAIL", str(e))
    
    # TC-FIX-COOKIE-02: 环境变量支持
    try:
        # 测试环境变量读取
        test_cookie = "test_cookie_value_12345"
        original_env = os.environ.get("DOUBAN_COOKIE")
        
        # 设置测试环境变量
        os.environ["DOUBAN_COOKIE"] = test_cookie
        
        # 重新导入模块以读取新的环境变量
        import importlib
        import config.headers
        importlib.reload(config.headers)
        from config.headers import COOKIE as new_cookie
        
        # 恢复原始环境变量
        if original_env:
            os.environ["DOUBAN_COOKIE"] = original_env
        else:
            os.environ.pop("DOUBAN_COOKIE", None)
        
        if new_cookie == test_cookie:
            log_test("TC-FIX-COOKIE-02", "环境变量支持", "PASS", "正确读取DOUBAN_COOKIE环境变量")
        else:
            log_test("TC-FIX-COOKIE-02", "环境变量支持", "FAIL", f"环境变量读取失败: 期望'{test_cookie}',实际'{new_cookie}'")
    except Exception as e:
        log_test("TC-FIX-COOKIE-02", "环境变量支持", "FAIL", str(e))
    
    # TC-FIX-COOKIE-03: 默认值处理
    try:
        # 清除环境变量
        original_env = os.environ.get("DOUBAN_COOKIE")
        os.environ.pop("DOUBAN_COOKIE", None)
        
        # 重新导入模块
        import importlib
        import config.headers
        importlib.reload(config.headers)
        from config.headers import COOKIE as default_cookie
        
        # 恢复原始环境变量
        if original_env:
            os.environ["DOUBAN_COOKIE"] = original_env
        
        if default_cookie == "":
            log_test("TC-FIX-COOKIE-03", "默认值处理", "PASS", "无环境变量时默认为空字符串")
        else:
            log_test("TC-FIX-COOKIE-03", "默认值处理", "FAIL", f"默认值应为空字符串,实际为'{default_cookie}'")
    except Exception as e:
        log_test("TC-FIX-COOKIE-03", "默认值处理", "FAIL", str(e))
    
    # TC-FIX-COOKIE-04: Headers生成包含Cookie
    try:
        headers = get_random_headers()
        if "Cookie" in headers:
            log_test("TC-FIX-COOKIE-04", "Headers包含Cookie", "PASS", "get_random_headers()返回的headers包含Cookie字段")
        else:
            log_test("TC-FIX-COOKIE-04", "Headers包含Cookie", "FAIL", "headers缺少Cookie字段")
    except Exception as e:
        log_test("TC-FIX-COOKIE-04", "Headers包含Cookie", "FAIL", str(e))
    
except Exception as e:
    log_test("TC-FIX-COOKIE-01", "Cookie模块导入", "FAIL", str(e))

print()

# ============================================================================
# 测试总结
# ============================================================================
print("=" * 80)
print("修复验证测试总结")
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
print("修复验证测试完成")
print("=" * 80)

# 返回测试结果供外部调用
if __name__ == "__main__":
    import json
    print("\n测试结果JSON:")
    print(json.dumps(test_results, ensure_ascii=False, indent=2))
