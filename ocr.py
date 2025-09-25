import os
import requests
from io import BytesIO
from paddleocr import PaddleOCR

def ocr_from_url(image_url):
    # 下载图片
    response = requests.get(image_url)
    img_data = BytesIO(response.content)
    
    # 初始化PaddleOCR（使用use_angle_cls替代cls参数）
    ocr = PaddleOCR(use_angle_cls=True, lang="ch")
    
    # 使用predict方法替代ocr方法
    result = ocr.predict(img_data)
    
    # 提取识别结果文本
    recognized_text = ' '.join([line[1][0] for line in result[0]])
    return recognized_text

# 图片URL
image_url = "https://www.stratesave.com/html/images/sidchgtrial.png"

# 识别并打印结果
result = ocr_from_url(image_url)
print("识别结果:")
print(result)

# 生成getsid.bat脚本
script_dir = os.path.dirname(os.path.abspath(__file__))

bat_content = f'''@echo off
cd %~dp0
sidchg64-3.0k.exe /KEY="{result}" /F /R /OD /RESETALLAPPS
'''

bat_path = os.path.join(script_dir, 'getsid.bat')
with open(bat_path, 'w') as f:
    f.write(bat_content)

print(f"已生成批处理脚本：{bat_path}")
