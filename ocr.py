import os
import requests
import easyocr
import cv2
import numpy as np
import re

def postprocess_result(text):
    """对OCR结果进行修正，合并符号 & 修复大小写"""
    
    # 1. 去掉多余空格和换行
    text = text.strip().replace("\n", "")
    
    # 2. 修复多余的@
    if text.count("@") > 1:
        # 只保留第一个
        first_idx = text.find("@")
        # 删除后面的@
        text = text[:first_idx+1] + text[first_idx+1:].replace("@", "")
    
    # 3. 修复常见大小写问题：WO → wo
    # 注意：这里可以根据你知道的真实格式进行更精确的替换规则
    text = text.replace("WOQEE", "woQEE")
    
    # 4. 进一步修复常见OCR错位问题 0/O, I/l
    corrections = {
        "OQ": "0Q",   # 有时候O被识别成0
        "l": "I",     # 小写l识别为大写I时修复
    }
    for wrong, right in corrections.items():
        text = text.replace(wrong, right)
    
    return text

def ocr_from_url(image_url):
    """使用EasyOCR识别并进行纠错"""
    try:
        # 初始化EasyOCR
        reader = easyocr.Reader(['en'], gpu=False)
        
        # 下载图片
        response = requests.get(image_url)
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        # OCR识别
        results = reader.readtext(img, detail=0, allowlist=None)
        raw_text = ''.join(results) if results else "识别失败"
        
        # 后处理修复
        fixed_text = postprocess_result(raw_text)
        
        return fixed_text
    
    except Exception as e:
        return f"OCR错误: {e}"

# ===== 主程序 =====
if __name__ == "__main__":
    image_url = "https://www.stratesave.com/html/images/sidchgtrial.png"
    
    # 识别并打印结果
    result = ocr_from_url(image_url)
    print("最终识别结果:")
    print(result)
    
    # 生成getsid.bat脚本
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    bat_content = f'''@echo off
cd %~dp0
sidchg64-3.0k.exe /KEY="{result}" /F /R /OD /RESETALLAPPS'''
    
    bat_path = os.path.join(script_dir, 'getsid.bat')
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    print(f"\ngetsid.bat文件已生成在: {bat_path}")
    print(f"文件内容:\n{bat_content}")
