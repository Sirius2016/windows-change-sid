import os
import requests
from PIL import Image
from io import BytesIO
import pytesseract

# 你要识别的图片 URL
image_url = "https://www.stratesave.com/html/images/sidchgtrial.png"

def ocr_from_url(url):
    # 下载图片
    response = requests.get(url)
    response.raise_for_status()
    img = Image.open(BytesIO(response.content))

    # 使用 pytesseract OCR 识别图像文字
    text = pytesseract.image_to_string(img, lang="eng")
    
    # 去掉前后空格和换行
    return text.strip()

# 识别并获取结果
result = ocr_from_url(image_url)
print("识别结果:")
print(result)

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 生成bat文件内容
bat_content = f'''@echo off
cd %~dp0
sidchg64-3.0k.exe /KEY="{result}" /F /R /OD /RESETALLAPPS'''

# 在脚本目录下生成getsid.bat文件
bat_path = os.path.join(script_dir, 'getsid.bat')
with open(bat_path, 'w', encoding="utf-8") as f:
    f.write(bat_content)

print(f"已生成 getsid.bat, 文件路径: {bat_path}")
