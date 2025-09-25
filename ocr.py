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
        print(f"正在下载图片: {image_url}")
        # 下载图片
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # 将图片内容转换为PIL Image对象
        image = Image.open(io.BytesIO(response.content))
        
        # 转换为numpy数组
        image_np = np.array(image)
        
        print("正在初始化OCR引擎...")
        # 初始化PaddleOCR - 使用最新版API
        ocr = PaddleOCR(lang='en')
        
        print("正在进行OCR识别...")
        # 执行OCR识别
        result = ocr.ocr(image_np)
        
        print("正在解析识别结果...")
        # 提取识别的文本
        extracted_text = ""
        
        # 处理OCR结果
        if result and len(result) > 0 and result[0]:
            for line in result[0]:
                if line and len(line) >= 2:
                    text_info = line[1]
                    if text_info and len(text_info) >= 1:
                        text = text_info[0]
                        if text and isinstance(text, str):
                            extracted_text += text + " "
        
        final_result = extracted_text.strip()
        print(f"识别完成，结果: '{final_result}'")
        return final_result
    
    except Exception as e:
        print(f"OCR识别过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return ""

def main():
    """
    主函数：执行OCR识别并生成bat脚本
    """
    # 图片URL
    image_url = "https://www.stratesave.com/html/images/sidchgtrial.png"
    
    print("=" * 60)
    print("OCR识别与脚本生成工具")
    print("=" * 60)
    
    # 识别并打印结果
    result = ocr_from_url(image_url)
    
    print("\n识别结果:")
    print("-" * 40)
    print(result)
    print("-" * 40)
    
    # 检查识别结果
    if not result:
        print("\n❌ OCR识别失败，无法生成脚本")
        return
    
    # 生成getsid.bat脚本
    print("\n正在生成getsid.bat脚本...")
    
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 生成bat文件内容
    bat_content = f'''@echo off
cd %~dp0
sidchg64-3.0k.exe /KEY="{result}" /F /R /OD /RESETALLAPP
'''
    
    # 在脚本目录下生成getsid.bat文件
    bat_path = os.path.join(script_dir, 'getsid.bat')
    
    try:
        with open(bat_path, 'w', encoding='utf-8') as f:
            f.write(bat_content)
        
        print(f"✅ 脚本生成成功!")
        print(f"脚本路径: {bat_path}")
        
        # 显示生成的脚本内容
        print("\n生成的脚本内容:")
        print("-" * 40)
        with open(bat_path, 'r', encoding='utf-8') as f:
            print(f.read())
        print("-" * 40)
        
        # 保存识别结果到文本文件
        result_path = os.path.join(script_dir, 'ocr_result.txt')
        with open(result_path, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"\n识别结果已保存到: {result_path}")
        
    except Exception as e:
        print(f"❌ 生成脚本时发生错误: {e}")
    
    print("\n" + "=" * 60)
    print("程序执行完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
