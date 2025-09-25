import os
import requests
from io import BytesIO
from PIL import Image
from paddleocr import PaddleOCR

def ocr_from_url(image_url):
    # 下载图片
    response = requests.get(image_url)
    # 初始化PaddleOCR
    ocr = PaddleOCR(use_angle_cls=True, lang="ch")
    # 识别图片
    result = ocr.ocr(BytesIO(response.content), use_angle_cls=True)
    # 提取识别结果
    recognized_text = ' '.join([line[1][0] for line in result])
    return recognized_text

# 图片URL
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
sidchg64-3.0k.exe /KEY="{result}" /F /R /OD /RESETALLAPPS
'''

# 在脚本目录下生成getsid.bat文件
bat_path = os.path.join(script_dir, 'getsid.bat')
with open(bat_path, 'w') as f:
    f.write(bat_content)

print(f"已生成批处理脚本：{bat_path}")
