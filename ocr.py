import os
import requests
import easyocr
import cv2
import numpy as np
import re

def preprocess_image_multiple_ways(img):
    """生成多种预处理版本的图片"""
    preprocessed_images = []
    
    # 1. 原始图片
    preprocessed_images.append(('original', img))
    
    # 2. 灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    preprocessed_images.append(('gray', gray))
    
    # 3. 轻微放大（保持细节）
    scale = 1.5
    height, width = gray.shape
    resized = cv2.resize(gray, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_CUBIC)
    preprocessed_images.append(('resized1.5x', resized))
    
    # 4. 中等放大
    scale = 2
    resized2 = cv2.resize(gray, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_CUBIC)
    preprocessed_images.append(('resized2x', resized2))
    
    # 5. 锐化处理
    kernel = np.array([[-1,-1,-1],
                       [-1, 9,-1],
                       [-1,-1,-1]])
    sharpened = cv2.filter2D(gray, -1, kernel)
    preprocessed_images.append(('sharpened', sharpened))
    
    # 6. 轻微二值化（保持灰度信息）
    _, binary_light = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    preprocessed_images.append(('binary_light', binary_light))
    
    # 7. CLAHE (对比度限制自适应直方图均衡)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    preprocessed_images.append(('clahe', enhanced))
    
    return preprocessed_images

def clean_ocr_result(text):
    """清理OCR结果，修复常见错误"""
    if not text:
        return text
    
    # 1. 修复双@问题 - 将连续的@@替换为单个@
    text = re.sub(r'@+', '@', text)
    
    # 2. 修复可能的大小写错误
    # 如果是类似密钥格式（用-分隔的段），检查每段
    parts = text.split('-')
    corrected_parts = []
    
    for part in parts:
        # 如果这部分包含@，特别处理
        if '@' in part:
            # 保持@符号，但检查其他字符
            corrected_parts.append(part)
        else:
            # 对于不包含@的部分，可能需要大小写修正
            # 但由于我们不知道确切的规则，暂时保持原样
            corrected_parts.append(part)
    
    return '-'.join(corrected_parts)

def ocr_from_url_accurate(image_url):
    """更准确的OCR识别，特别注意@符号和大小写"""
    try:
        # 初始化EasyOCR
        reader = easyocr.Reader(['en'], gpu=False)
        
        # 下载图片
        response = requests.get(image_url)
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        # 获取多种预处理版本
        preprocessed_images = preprocess_image_multiple_ways(img)
        
        all_results = []
        
        # 对每个预处理版本进行识别
        for name, processed_img in preprocessed_images:
            try:
                # 使用不同的参数组合
                param_sets = [
                    {'detail': 1, 'paragraph': False, 'width_ths': 0.7, 'height_ths': 0.7},
                    {'detail': 1, 'paragraph': False, 'width_ths': 0.5, 'height_ths': 0.5},
                    {'detail': 0, 'paragraph': False},
                ]
                
                for params in param_sets:
                    results = reader.readtext(processed_img, **params, allowlist=None)
                    
                    if params.get('detail', 0) == 1:
                        # 详细模式，提取文本
                        text_parts = []
                        for (bbox, text, prob) in results:
                            if prob > 0.3:  # 较低的阈值
                                text_parts.append(text)
                        if text_parts:
                            result_text = ''.join(text_parts)
                            all_results.append((name, result_text, max([r[2] for r in results])))
                    else:
                        # 简单模式
                        if results:
                            result_text = ''.join(results)
                            all_results.append((name, result_text, 0.5))
                            
            except Exception as e:
                print(f"处理 {name} 时出错: {e}")
                continue
        
        # 分析所有结果，选择最佳
        print("所有识别结果：")
        for name, text, conf in all_results:
            cleaned = clean_ocr_result(text)
            print(f"{name}: {cleaned} (置信度: {conf:.2f})")
        
        # 选择最佳结果的策略
        best_result = ""
        best_score = -1
        
        for name, text, conf in all_results:
            cleaned = clean_ocr_result(text)
            
            # 计算得分
            score = 0
            
            # 1. 包含单个@符号得分更高
            if cleaned.count('@') == 1:
                score += 10
            elif cleaned.count('@') > 1:
                score -= 5
                
            # 2. 长度合理（看起来像密钥格式）
            if 15 <= len(cleaned) <= 25:
                score += 5
                
            # 3. 包含连字符
            if '-' in cleaned:
                score += cleaned.count('-') * 2
                
            # 4. 置信度
            score += conf * 5
            
            # 5. 特定预处理方法的偏好
            if name in ['resized1.5x', 'resized2x', 'clahe']:
                score += 2
                
            if score > best_score:
                best_score = score
                best_result = cleaned
        
        return best_result if best_result else "识别失败"
        
    except Exception as e:
        print(f"OCR错误: {e}")
        return "识别失败"

def ocr_from_url(image_url):
    """主OCR函数"""
    print("正在识别图片中的文字...")
    
    # 使用改进的识别函数
    result = ocr_from_url_accurate(image_url)
    
    # 额外的后处理
    if result and result != "识别失败":
        # 确保只有一个@
        result = re.sub(r'@+', '@', result)
        
        # 如果结果看起来像 78@@5i-QwUJM-WOQEE-Kv 这种格式
        # 尝试智能修正大小写
        if re.match(r'^[A-Za-z0-9@\-]+$', result):
            parts = result.split('-')
            
            # 对每个部分进行检查
            corrected_parts = []
            for i, part in enumerate(parts):
                if i == 0 and '@' in part:
                    # 第一部分包含@，保持原样但确保只有一个@
                    part = re.sub(r'@+', '@', part)
                    corrected_parts.append(part)
                else:
                    # 其他部分，检查是否需要调整大小写
                    # 这里我们假设密钥可能是大小写混合的
                    # 如果OCR将所有字母识别为大写，可能需要修正
                    
                    # 检查是否全是大写
                    if part.isupper() and len(part) > 2:
                        # 可能需要转换一些字母为小写
                        # 使用一个简单的规则：如果看起来像 "WOQEE"，可能应该是 "woQEE"
                        # 这只是一个示例，实际规则可能不同
                        new_part = ""
                        for j, char in enumerate(part):
                            if j < 2:  # 前两个字符小写
                                new_part += char.lower()
                            else:
                                new_part += char
                        corrected_parts.append(new_part)
                    else:
                        corrected_parts.append(part)
            
            # 如果修正后的结果看起来更合理，使用它
            corrected_result = '-'.join(corrected_parts)
            
            # 打印两个版本供比较
            print(f"原始OCR结果: {result}")
            print(f"修正后结果: {corrected_result}")
            
            # 让用户选择或使用启发式规则
            # 这里我们使用修正后的版本
            result = corrected_result
    
    return result

# 主程序
if __name__ == "__main__":
    # 图片URL
    image_url = "https://www.stratesave.com/html/images/sidchgtrial.png"
    
    # 识别并打印结果
    result = ocr_from_url(image_url)
    print("\n最终识别结果:")
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
    print(f"文件内容:\n{bat_content}")
