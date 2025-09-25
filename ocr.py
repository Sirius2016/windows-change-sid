import os
import sys
import requests
import cv2
import numpy as np
from io import BytesIO
from paddleocr import PaddleOCR

def ocr_from_url(image_url):
    try:
        # 下载图片
        print("正在下载图片...")
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()  # 检查HTTP错误
        
        # 检查内容类型
        content_type = response.headers.get('content-type', '')
        if 'image' not in content_type:
            raise ValueError(f"URL未返回图片内容 (Content-Type: {content_type})")
        
        # 转换图片为OpenCV格式
        print("正在处理图片...")
        img = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("无法解码图片数据")
        
        # 初始化PaddleOCR
        print("正在初始化OCR引擎...")
        ocr = PaddleOCR(use_angle_cls=True, lang="ch")
        
        # 执行OCR识别
        print("正在进行文字识别...")
        result = ocr.predict(img)
        
        # 处理识别结果
        if not result or not any(result):
            raise ValueError("未识别到任何文字")
        
        print(f"原始识别结果: {result}")
        recognized_text = ' '.join([line[1][0] for line in result[0] if line and len(line) > 1])
        
        if not recognized_text.strip():
            raise ValueError("识别结果为空")
        
        return recognized_text
    
    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {str(e)}")
    except ValueError as e:
        print(f"数据处理错误: {str(e)}")
    except cv2.error as e:
        print(f"OpenCV处理错误: {str(e)}")
    except Exception as e:
        print(f"OCR处理失败: {str(e)}")
    
    return None

# 主程序
if __name__ == "__main__":
    # 图片URL
    image_url = "https://www.stratesave.com/html/images/sidchgtrial.png"
    
    # 识别图片文字
    result = ocr_from_url(image_url)
    
    if result is None:
        print("错误: 无法获取有效的识别结果")
        sys.exit(1)
    
    print("\n识别结果:")
    print("-" * 40)
    print(result)
    print("-" * 40)
    
    # 生成getsid.bat脚本
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bat_content = f'''@echo off
cd %~dp0
echo 正在应用识别结果: {result}
sidchg64-3.0k.exe /KEY="{result}" /F /R /OD /RESETALLAPPS
echo 操作已完成，按任意键退出...
pause >nul
'''
        
        bat_path = os.path.join(script_dir, 'getsid.bat')
        with open(bat_path, 'w', encoding='gbk') as f:
            f.write(bat_content)
        
        print(f"\n成功生成批处理脚本: {bat_path}")
        
    except PermissionError:
        print("错误: 没有写入权限，请以管理员身份运行脚本")
        sys.exit(1)
    except OSError as e:
        print(f"文件操作错误: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"生成脚本时出错: {str(e)}")
        sys.exit(1)
