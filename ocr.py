import os
import requests
from paddleocr import PaddleOCR
from PIL import Image
import io
import numpy as np

def ocr_from_url(image_url):
    """
    从URL下载图片并进行OCR识别
    """
    try:
        # 下载图片
        response = requests.get(image_url)
        response.raise_for_status()
        
        # 将图片内容转换为PIL Image对象
        image = Image.open(io.BytesIO(response.content))
        
        # 转换为numpy数组
        image_np = np.array(image)
        
        # 初始化PaddleOCR
        ocr = PaddleOCR(use_angle_cls=True, lang='en')  # 使用英文识别
        
        # 使用新的predict API进行OCR识别
        result = ocr.predict(image_np)
        
        # 提取识别的文本
        extracted_text = ""
        if result and len(result) > 0:
            for line in result:
                if hasattr(line, '__len__') and len(line) > 1:
                    # 新版本的返回格式可能不同，需要适配
                    if isinstance(line[1], (list, tuple)) and len(line[1]) > 0:
                        text = line[1][0]
                        if text:
                            extracted_text += text + " "
                    elif isinstance(line[1], str):
                        extracted_text += line[1] + " "
        
        return extracted_text.strip()
    
    except Exception as e:
        print(f"OCR识别过程中发生错误: {e}")
        return ""

def ocr_from_url_fallback(image_url):
    """
    备用OCR识别方法，使用旧版API兼容方式
    """
    try:
        # 下载图片
        response = requests.get(image_url)
        response.raise_for_status()
        
        # 将图片内容转换为PIL Image对象
        image = Image.open(io.BytesIO(response.content))
        
        # 初始化PaddleOCR
        ocr = PaddleOCR(use_angle_cls=True, lang='en')
        
        # 尝试使用ocr方法（如果存在）
        if hasattr(ocr, 'ocr'):
            result = ocr.ocr(image, cls=True)
            
            # 提取识别的文本
            extracted_text = ""
            if result and result[0]:
                for line in result[0]:
                    if line[1][0]:  # 检查文本是否为空
                        extracted_text += line[1][0] + " "
            
            return extracted_text.strip()
        else:
            return ""
    
    except Exception as e:
        print(f"备用OCR识别方法也失败: {e}")
        return ""

def generate_bat_script(result_text):
    """
    生成getsid.bat脚本
    """
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 生成bat文件内容
    bat_content = f'''@echo off
cd %~dp0
sidchg64-3.0k.exe /KEY="{result_text}" /F /R /OD /RESETALLAPP
'''
    
    # 在脚本目录下生成getsid.bat文件
    bat_path = os.path.join(script_dir, 'getsid.bat')
    
    try:
        with open(bat_path, 'w', encoding='utf-8') as f:
            f.write(bat_content)
        print(f"成功生成bat脚本: {bat_path}")
        return bat_path
    except Exception as e:
        print(f"生成bat脚本时发生错误: {e}")
        return None

def main():
    """
    主函数
    """
    # 图片URL
    image_url = "https://www.stratesave.com/html/images/sidchgtrial.png"
    
    print("开始OCR识别...")
    print(f"图片URL: {image_url}")
    
    # 尝试新版API
    result = ocr_from_url(image_url)
    
    # 如果新版失败，尝试旧版API
    if not result:
        print("新版API失败，尝试备用方法...")
        result = ocr_from_url_fallback(image_url)
    
    print("识别结果:")
    print(f"'{result}'")
    
    if result:
        # 生成getsid.bat脚本
        bat_path = generate_bat_script(result)
        
        if bat_path:
            print(f"\n脚本生成完成！")
            print(f"识别的文本已保存到变量: result = '{result}'")
            print(f"生成的bat脚本: {bat_path}")
            
            # 显示生成的bat内容
            print(f"\n生成的bat脚本内容:")
            with open(bat_path, 'r', encoding='utf-8') as f:
                print(f.read())
        else:
            print("bat脚本生成失败")
    else:
        print("OCR识别失败，无法生成bat脚本")

if __name__ == "__main__":
    main()
