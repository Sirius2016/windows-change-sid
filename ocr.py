import os
import requests
import easyocr
import cv2
import numpy as np

def ocr_from_url(image_url):
    """识别包含特殊字符的图片文字"""
    try:
        # 初始化EasyOCR，不限制字符集
        reader = easyocr.Reader(['en'], gpu=False)
        
        # 下载图片
        response = requests.get(image_url)
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        # 尝试多种方式识别
        results_list = []
        
        # 1. 直接识别原图
        results = reader.readtext(img, detail=0, allowlist=None)
        if results:
            results_list.append(''.join(results))
        
        # 2. 灰度图识别
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        results = reader.readtext(gray, detail=0, allowlist=None)
        if results:
            results_list.append(''.join(results))
        
        # 3. 放大后识别
        scale = 2
        resized = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        results = reader.readtext(resized, detail=0, allowlist=None)
        if results:
            results_list.append(''.join(results))
        
        # 选择最佳结果
        best_result = ""
        for result in results_list:
            # 优先选择包含@的结果
            if '@' in result:
                return result
            # 否则选择最长的
            if len(result) > len(best_result):
                best_result = result
        
        # 如果没有找到@，尝试智能替换
        if best_result and '@' not in best_result:
            # 查找可能被误识别为其他字符的@
            # 常见模式：字母数字 + 特殊字符 + 字母数字
            import re
            # 尝试找到类似邮箱的模式
            pattern = r'([A-Za-z0-9]+)([^A-Za-z0-9\s])([A-Za-z0-9]+)'
            match = re.search(pattern, best_result)
            if match:
                # 替换中间的字符为@
                best_result = best_result[:match.start(2)] + '@' + best_result[match.end(2):]
        
        return best_result
        
    except Exception as e:
        print(f"OCR错误: {e}")
        return "识别失败"

# 图片URL
image_url = "https://www.stratesave.com/html/images/sidchgtrial.png"

# 识别并打印结果
result = ocr_from_url(image_url)
print("识别结果:")
print(result)

# 生成getsid.bat脚本
script_dir = os.path.dirname(os.path.abspath(__file__))

# 生成bat文件内容
bat_content = f'''@echo off
cd %~dp0
sidchg64-3.0k.exe /KEY="{result}" /F /R /OD /RESETALLAPPS'''

# 在脚本目录下生成getsid.bat文件
bat_path = os.path.join(script_dir, 'getsid.bat')
with open(bat_path, 'w', encoding='utf-8') as f:
    f.write(bat_content)

print(f"\ngetsid.bat文件已生成在: {bat_path}")
