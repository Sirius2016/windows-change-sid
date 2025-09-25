import os
import requests
from PIL import Image
from io import BytesIO
import pytesseract
import easyocr
import cv2
import numpy as np

def ocr_from_url_tesseract(image_url):
    """使用Tesseract OCR识别图片中的文字"""
    try:
        # 下载图片
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        
        # 转换为RGB模式（如果需要）
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 使用Tesseract进行OCR识别
        result = pytesseract.image_to_string(img, lang='eng')
        return result.strip()
    except Exception as e:
        print(f"Tesseract OCR错误: {e}")
        return None

def ocr_from_url_easyocr(image_url):
    """使用EasyOCR识别图片中的文字"""
    try:
        # 初始化EasyOCR读取器
        reader = easyocr.Reader(['en'])
        
        # 下载图片
        response = requests.get(image_url)
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        # 进行OCR识别
        results = reader.readtext(img)
        
        # 提取文本
        text_list = [item[1] for item in results]
        return ' '.join(text_list).strip()
    except Exception as e:
        print(f"EasyOCR错误: {e}")
        return None

def preprocess_image(image_url):
    """预处理图片以提高OCR识别率"""
    try:
        # 下载图片
        response = requests.get(image_url)
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 应用阈值处理
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 去噪
        denoised = cv2.medianBlur(thresh, 3)
        
        # 转换回PIL Image
        pil_img = Image.fromarray(denoised)
        
        # 使用Tesseract进行OCR识别
        result = pytesseract.image_to_string(pil_img, lang='eng', config='--psm 6')
        return result.strip()
    except Exception as e:
        print(f"图片预处理错误: {e}")
        return None

def ocr_from_url(image_url):
    """综合OCR函数，尝试多种方法"""
    print("正在识别图片中的文字...")
    
    # 方法1: 使用预处理的Tesseract
    result = preprocess_image(image_url)
    if result:
        print("使用预处理Tesseract识别成功")
        return result
    
    # 方法2: 直接使用Tesseract
    result = ocr_from_url_tesseract(image_url)
    if result:
        print("使用Tesseract识别成功")
        return result
    
    # 方法3: 使用EasyOCR
    result = ocr_from_url_easyocr(image_url)
    if result:
        print("使用EasyOCR识别成功")
        return result
    
    return "OCR识别失败"

# 主程序
if __name__ == "__main__":
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
sidchg64-3.0k.exe /KEY="{result}" /F /R /OD /RESETALLAPPS'''
    
    # 在脚本目录下生成getsid.bat文件
    bat_path = os.path.join(script_dir, 'getsid.bat')
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    print(f"\ngetsid.bat文件已生成在: {bat_path}")
