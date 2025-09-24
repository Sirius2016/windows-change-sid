import os
import requests
from paddleocr import PaddleOCR
from PIL import Image
import io
import numpy as np

def ocr_from_url(image_url):
    """
    从URL下载图片并进行OCR识别 - 使用新版PaddleOCR API
    """
    try:
        print("正在下载图片...")
        # 下载图片
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # 将图片内容转换为PIL Image对象
        image = Image.open(io.BytesIO(response.content))
        
        # 转换为numpy数组
        image_np = np.array(image)
        
        print("正在初始化PaddleOCR...")
        # 初始化PaddleOCR - 使用新版API
        ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
        
        print("正在进行OCR识别...")
        # 使用新版API进行识别
        result = ocr.ocr(image_np)
        
        print("正在解析识别结果...")
        # 提取识别的文本 - 新版API返回格式处理
        extracted_text = ""
        
        # 新版PaddleOCR返回格式: [[[[box], [text, confidence]]]]
        if result and len(result) > 0:
            for line in result[0]:
                if line and len(line) >= 2:
                    text_info = line[1]
                    if text_info and len(text_info) >= 1:
                        text = text_info[0]
                        if text and isinstance(text, str):
                            extracted_text += text + " "
        
        final_result = extracted_text.strip()
        print(f"提取的文本: '{final_result}'")
        return final_result
    
    except Exception as e:
        print(f"OCR识别过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return ""

def ocr_from_url_simple(image_url):
    """
    简化版OCR识别方法
    """
    try:
        print("使用简化方法进行OCR识别...")
        
        # 下载并保存图片
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        temp_image_path = "temp_ocr_image.png"
        with open(temp_image_path, 'wb') as f:
            f.write(response.content)
        
        print("图片已保存到临时文件")
        
        # 使用命令行方式调用paddleocr
        import subprocess
        cmd = ['python', '-m', 'paddleocr', '--image_dir', temp_image_path, '--lang', 'en']
        
        print("执行命令行OCR...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        # 删除临时文件
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        
        if result.returncode == 0:
            # 解析命令行输出
            output_lines = result.stdout.split('\n')
            extracted_text = ""
            
            for line in output_lines:
                line = line.strip()
                if line and not line.startswith('WARNING') and not line.startswith('['):
                    # 简单的文本提取逻辑
                    if len(line) > 3:  # 过滤掉太短的行
                        extracted_text += line + " "
            
            final_result = extracted_text.strip()
            print(f"命令行OCR结果: '{final_result}'")
            return final_result
        else:
            print(f"命令行OCR错误: {result.stderr}")
            return ""
    
    except Exception as e:
        print(f"简化版OCR方法失败: {e}")
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
    
    print("=" * 50)
    print("PaddleOCR 图片文字识别工具")
    print("=" * 50)
    print(f"图片URL: {image_url}")
    print()
    
    # 尝试新版API
    result = ocr_from_url(image_url)
    
    # 如果新版失败，尝试命令行方法
    if not result:
        print("新版API失败，尝试命令行方法...")
        result = ocr_from_url_simple(image_url)
    
    print("\n" + "=" * 50)
    print("识别结果:")
    print("=" * 50)
    print(f"'{result}'")
    
    if result:
        # 生成getsid.bat脚本
        bat_path = generate_bat_script(result)
        
        if bat_path:
            print(f"\n✅ 脚本生成完成！")
            print(f"识别的文本已保存到变量: result = '{result}'")
            print(f"生成的bat脚本: {bat_path}")
            
            # 显示生成的bat内容
            print(f"\n📄 生成的bat脚本内容:")
            print("-" * 30)
            with open(bat_path, 'r', encoding='utf-8') as f:
                print(f.read())
            print("-" * 30)
        else:
            print("❌ bat脚本生成失败")
    else:
        print("❌ OCR识别失败，无法生成bat脚本")
    
    print("\n" + "=" * 50)
    print("程序执行完成")
    print("=" * 50)

if __name__ == "__main__":
    main()
