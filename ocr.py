import os
import requests
import cv2
import numpy as np
import pytesseract
from PIL import Image
from io import BytesIO
import re

def ocr_from_url(image_url):
    """使用Tesseract进行更准确的OCR"""
    try:
        # 下载图片
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        
        # 转换为numpy数组进行预处理
        img_array = np.array(img)
        
        # 如果是彩色图片，转换为灰度
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # 放大图片
        scale = 2
        height, width = gray.shape
        resized = cv2.resize(gray, (width * scale, height * scale), interpolation=cv2.INTER_CUBIC)
        
        # 转回PIL Image
        pil_img = Image.fromarray(resized)
        
        # 使用Tesseract，不限制字符
        custom_config = r'--oem 3 --psm 8'
        result = pytesseract.image_to_string(pil_img, config=custom_config)
        
        # 清理结果
        result = result.strip()
        # 修复双@问题
        result = re.sub(r'@+', '@', result)
        # 去除多余的空格
        result = re.sub(r'\s+', '', result)
        
        return result
        
    except Exception as e:
        print(f"Tesseract OCR错误: {e}")
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
