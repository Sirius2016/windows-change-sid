import os
import requests
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import pytesseract
import easyocr
import re

def preprocess_for_ocr(img_array):
    """增强的图片预处理函数"""
    # 转换为灰度图
    gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
    
    # 放大图片以提高识别率
    scale_factor = 3
    width = int(gray.shape[1] * scale_factor)
    height = int(gray.shape[0] * scale_factor)
    resized = cv2.resize(gray, (width, height), interpolation=cv2.INTER_CUBIC)
    
    # 应用高斯模糊去噪
    blurred = cv2.GaussianBlur(resized, (5, 5), 0)
    
    # 应用自适应阈值
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    
    # 形态学操作
    kernel = np.ones((2, 2), np.uint8)
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # 反转颜色（如果需要）
    # 检查是否大部分是黑色背景
    if np.mean(morph) < 127:
        morph = cv2.bitwise_not(morph)
    
    return morph

def ocr_with_easyocr_enhanced(image_url):
    """增强的EasyOCR识别"""
    try:
        # 初始化EasyOCR，添加更多参数
        reader = easyocr.Reader(['en'], gpu=False)
        
        # 下载图片
        response = requests.get(image_url)
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        # 预处理图片
        processed = preprocess_for_ocr(img)
        
        # 使用EasyOCR识别，调整参数
        results = reader.readtext(processed, 
                                detail=1,
                                paragraph=False,
                                width_ths=0.7,
                                height_ths=0.7,
                                text_threshold=0.5,
                                low_text=0.3)
        
        # 提取并清理文本
        text_list = []
        for (bbox, text, prob) in results:
            # 只保留置信度较高的结果
            if prob > 0.3:
                # 清理文本：只保留字母数字和常见符号
                cleaned_text = re.sub(r'[^A-Za-z0-9\-_]', '', text)
                if cleaned_text:
                    text_list.append(cleaned_text)
        
        result = ''.join(text_list)
        return result if result else None
        
    except Exception as e:
        print(f"EasyOCR增强版错误: {e}")
        return None

def ocr_with_tesseract_enhanced(image_url):
    """增强的Tesseract识别"""
    try:
        # 下载图片
        response = requests.get(image_url)
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        # 预处理图片
        processed = preprocess_for_ocr(img)
        
        # 转换为PIL Image
        pil_img = Image.fromarray(processed)
        
        # 使用多种配置尝试识别
        configs = [
            '--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-',
            '--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-',
            '--psm 6',
            '--psm 11',
            '--psm 13'
        ]
        
        best_result = ""
        for config in configs:
            try:
                result = pytesseract.image_to_string(pil_img, lang='eng', config=config)
                result = result.strip().replace(' ', '').replace('\n', '')
                if len(result) > len(best_result):
                    best_result = result
            except:
                continue
        
        return best_result if best_result else None
        
    except Exception as e:
        print(f"Tesseract增强版错误: {e}")
        return None

def try_multiple_preprocessing(image_url):
    """尝试多种预处理方法"""
    try:
        response = requests.get(image_url)
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        results = []
        
        # 方法1: 原始图片
        reader = easyocr.Reader(['en'], gpu=False)
        result1 = reader.readtext(img, detail=0)
        if result1:
            results.append(''.join(result1))
        
        # 方法2: 灰度+二值化
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        result2 = reader.readtext(binary, detail=0)
        if result2:
            results.append(''.join(result2))
        
        # 方法3: 反转颜色
        inverted = cv2.bitwise_not(gray)
        result3 = reader.readtext(inverted, detail=0)
        if result3:
            results.append(''.join(result3))
        
        # 返回最长的结果
        if results:
            return max(results, key=len)
        return None
        
    except Exception as e:
        print(f"多重预处理错误: {e}")
        return None

def ocr_from_url(image_url):
    """综合OCR函数"""
    print("正在识别图片中的文字...")
    
    # 方法1: 增强的EasyOCR
    print("尝试方法1: 增强的EasyOCR...")
    result = ocr_with_easyocr_enhanced(image_url)
    if result and len(result) > 5:  # 假设有效结果至少5个字符
        print(f"EasyOCR识别成功: {result}")
        return result
    
    # 方法2: 增强的Tesseract
    print("尝试方法2: 增强的Tesseract...")
    result = ocr_with_tesseract_enhanced(image_url)
    if result and len(result) > 5:
        print(f"Tesseract识别成功: {result}")
        return result
    
    # 方法3: 多重预处理
    print("尝试方法3: 多重预处理...")
    result = try_multiple_preprocessing(image_url)
    if result and len(result) > 5:
        print(f"多重预处理识别成功: {result}")
        return result
    
    # 如果都失败，尝试手动查看图片特征
    print("\n自动识别失败，尝试显示图片信息...")
    try:
        response = requests.get(image_url)
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        print(f"图片尺寸: {img.shape}")
        
        # 保存预处理后的图片供调试
        processed = preprocess_for_ocr(img)
        cv2.imwrite('processed_image.png', processed)
        print("已保存预处理后的图片为 processed_image.png，请检查")
    except:
        pass
    
    return "OCR识别失败"

# 主程序
if __name__ == "__main__":
    # 确保已安装Tesseract
    try:
        # Windows用户可能需要指定路径
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    except:
        pass
    
    # 图片URL
    image_url = "https://www.stratesave.com/html/images/sidchgtrial.png"
    
    # 识别并打印结果
    result = ocr_from_url(image_url)
    print("\n最终识别结果:")
    print(result)
    
    # 清理结果（去除可能的空格和特殊字符）
    result = re.sub(r'[^A-Za-z0-9\-_]', '', result)
    print(f"清理后的结果: {result}")
    
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
    print(f"文件内容:\n{bat_content}")
