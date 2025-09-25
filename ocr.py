import os
import requests
from paddleocr import PaddleOCR
from PIL import Image
import io
import numpy as np
import subprocess
import tempfile

def ocr_from_url(image_url):
    """
    从URL下载图片并进行OCR识别 - 使用最新版PaddleOCR API
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
        # 初始化PaddleOCR - 使用最新版API参数
        ocr = PaddleOCR(
            use_textline_orientation=True,  # 替代已弃用的use_angle_cls
            lang='en'
        )
        
        print("正在进行OCR识别...")
        # 使用最新版API进行识别
        result = ocr.ocr(image_np)
        
        print("正在解析识别结果...")
        # 提取识别的文本 - 最新版API返回格式处理
        extracted_text = ""
        
        # PaddleOCR最新版返回格式: [[[[box], [text, confidence]]]]
        if result and len(result) > 0 and result[0]:
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

def ocr_from_url_cmd(image_url):
    """
    使用命令行方式调用PaddleOCR - 适配新版命令行格式
    """
    try:
        print("使用命令行方法进行OCR识别...")
        
        # 下载图片
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_image_path = temp_file.name
            temp_file.write(response.content)
        
        print(f"图片已保存到临时文件: {temp_image_path}")
        
        # 使用新版命令行格式调用paddleocr
        cmd = [
            'python', '-m', 'paddleocr', 'ocr',
            '--image_path', temp_image_path,
            '--lang', 'en',
            '--use_textline_orientation', 'true'
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # 删除临时文件
        try:
            os.unlink(temp_image_path)
        except:
            pass
        
        if result.returncode == 0:
            # 解析命令行输出
            output = result.stdout
            print(f"命令行输出: {output}")
            
            # 简单提取文本（过滤掉警告和调试信息）
            lines = output.split('\n')
            extracted_text = ""
            
            for line in lines:
                line = line.strip()
                # 跳过空行、警告和调试信息
                if (line and 
                    not line.startswith('WARNING') and 
                    not line.startswith('[') and
                    not line.startswith('---') and
                    not line.startswith('predict') and
                    len(line) > 3):
                    extracted_text += line + " "
            
            final_result = extracted_text.strip()
            print(f"命令行OCR提取结果: '{final_result}'")
            return final_result
        else:
            print(f"命令行OCR错误: {result.stderr}")
            return ""
    
    except Exception as e:
        print(f"命令行OCR方法失败: {e}")
        import traceback
        traceback.print_exc()
        return ""

def ocr_from_url_simple(image_url):
    """
    最简化的OCR方法 - 直接使用PaddleOCR的OCR类
    """
    try:
        print("使用简化方法进行OCR识别...")
        
        # 下载图片
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_image_path = temp_file.name
            temp_file.write(response.content)
        
        # 尝试最简单的初始化方式
        ocr = PaddleOCR(lang='en')
        
        # 读取图片
        result = ocr.ocr(temp_image_path)
        
        # 清理临时文件
        try:
            os.unlink(temp_image_path)
        except:
            pass
        
        # 提取文本
        extracted_text = ""
        if result and len(result) > 0 and result[0]:
            for line in result[0]:
                if line and len(line) >= 2:
                    text_info = line[1]
                    if text_info and len(text_info) >= 1:
                        text = text_info[0]
                        if text:
                            extracted_text += text + " "
        
        final_result = extracted_text.strip()
        print(f"简化方法结果: '{final_result}'")
        return final_result
        
    except Exception as e:
        print(f"简化OCR方法失败: {e}")
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
    
    print("=" * 60)
    print("PaddleOCR 图片文字识别工具 (最新版兼容)")
    print("=" * 60)
    print(f"图片URL: {image_url}")
    print()
    
    # 尝试多种方法
    result = ""
    methods_tried = []
    
    # 方法1: 最新版API
    methods_tried.append("最新版API")
    result = ocr_from_url(image_url)
    
    # 方法2: 命令行方式
    if not result:
        methods_tried.append("命令行方式")
        result = ocr_from_url_cmd(image_url)
    
    # 方法3: 简化方法
    if not result:
        methods_tried.append("简化方法")
        result = ocr_from_url_simple(image_url)
    
    print("\n" + "=" * 60)
    print("识别结果:")
    print("=" * 60)
    print(f"尝试的方法: {', '.join(methods_tried)}")
    print(f"最终结果: '{result}'")
    
    if result:
        # 生成getsid.bat脚本
        bat_path = generate_bat_script(result)
        
        if bat_path:
            print(f"\n✅ 脚本生成完成！")
            print(f"识别的文本已保存到变量: result = '{result}'")
            print(f"生成的bat脚本: {bat_path}")
            
            # 显示生成的bat内容
            print(f"\n📄 生成的bat脚本内容:")
            print("-" * 40)
            with open(bat_path, 'r', encoding='utf-8') as f:
                print(f.read())
            print("-" * 40)
        else:
            print("❌ bat脚本生成失败")
    else:
        print("❌ OCR识别失败，无法生成bat脚本")
        print("💡 建议检查网络连接或尝试其他图片")
    
    print("\n" + "=" * 60)
    print("程序执行完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
