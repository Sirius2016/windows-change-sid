import requests
from PIL import Image
import pytesseract
from io import BytesIO
import os

def ocr_from_url(url):
    """从URL获取图片并进行OCR识别"""
    try:
        # 下载图片
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        
        # OCR识别
        text = pytesseract.image_to_string(image, lang='eng')
        return text.strip()
    except Exception as e:
        return f"识别失败: {str(e)}"

# 目标图片URL
image_url = "https://www.stratesave.com/html/images/sidchgtrial.png"

# 识别并打印结果
result = ocr_from_url(image_url)
print("识别结果:")
print(result)

# 生成getsid.bat脚本
# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 生成bat文件内容
bat_content = f'''@echo off
cd %~dp0
sidchg64-3.0k.exe /KEY="{result}" /F /R /OD /RESETALLAPPS'''

# 在脚本目录下生成getsid.bat文件
bat_path = os.path.join(script_dir, 'getsid.bat')
with open(bat_path, 'w') as f:
    f.write(bat_content)
