#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
字体路径查找功能独立测试
"""

import os
import platform

def get_chinese_font_path():
    """
    获取中文字体路径
    
    优先级:
    1. 项目字体文件
    2. 系统字体
    
    Returns:
        str or None: 字体路径,未找到返回None
    """
    # 优先使用项目字体
    font_path = "assets/simhei.ttf"
    if os.path.exists(font_path):
        return font_path
    
    # 使用系统字体
    system = platform.system()
    
    if system == "Darwin":  # macOS
        system_fonts = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc"
        ]
    elif system == "Windows":
        system_fonts = [
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simsun.ttc"
        ]
    elif system == "Linux":
        system_fonts = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
        ]
    else:
        return None
    
    # 查找第一个存在的系统字体
    for font in system_fonts:
        if os.path.exists(font):
            return font
    
    return None

# 测试字体查找功能
print("=" * 80)
print("字体路径查找功能测试")
print("=" * 80)
print()

font_path = get_chinese_font_path()
print(f"当前系统: {platform.system()}")
print(f"找到的字体路径: {font_path}")

if font_path:
    if os.path.exists(font_path):
        print(f"✓ 字体文件存在: {font_path}")
    else:
        print(f"✗ 字体文件不存在: {font_path}")
else:
    print("✗ 未找到任何中文字体")

print()
print("=" * 80)
