import requests
from io import BytesIO
import os
import subprocess
import sys
import tempfile
import json

def ocr_from_url(url):
    """从URL获取图片并使用paddleocr命令行工具进行OCR识别"""
    temp_image_path = None
    try:
        # 1. 下载图片
        print(f"正在下载图片: {url}")
        response = requests.get(url)
        response.raise_for_status() # 检查请求是否成功

        # 2. 创建临时文件保存图片
        # 使用 tempfile.NamedTemporaryFile 可以自动管理临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_img:
            tmp_img.write(response.content)
            temp_image_path = tmp_img.name
        print(f"图片已保存到临时文件: {temp_image_path}")

        # 3. 构建paddleocr命令
        # 使用 --print_draw_res_dir=./temp_res 可以避免创建不必要的可视化文件
        # -o 指定输出目录，我们用一个临时目录处理结果
        # 我们将结果直接输出到标准输出，方便捕获
        # 注意：直接使用命令行工具可能输出多种格式，需要解析
        # 最可靠的方式是使用 --output_format 和 --save_file
        # 但这里我们尝试解析标准输出
        cmd = [
            sys.executable, '-m', 'paddleocr',
            '--image_dir', temp_image_path,
            '--lang', 'en',
            '--use_angle_cls', 'True', # 注意：如果这个参数也报错，请移除或替换为 use_textline_orientation
            '--show_log', 'False'      # 注意：如果这个参数也报错，请移除
        ]
        print(f"执行OCR命令: {' '.join(cmd)}")

        # 4. 执行OCR命令并捕获输出
        # 使用 capture_output=True 可以捕获 stdout 和 stderr
        # text=True 使输出为字符串而不是字节
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # 5. 解析输出
        # paddleocr 命令行的默认输出格式比较复杂且不易解析
        # 一种可靠的方法是让它输出 JSON 格式
        # 修改命令以输出 JSON 到文件
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as tmp_output:
            output_json_path = tmp_output.name

        cmd_json = [
            sys.executable, '-m', 'paddleocr',
            '--image_dir', temp_image_path,
            '--lang', 'en',
            '--use_angle_cls', 'True', 
            '--show_log', 'False',
            '--output_format', 'JSON', # 指定输出格式
            '--save_file', output_json_path # 保存到文件
        ]
        print(f"执行OCR命令 (JSON输出): {' '.join(cmd_json)}")
        result_json = subprocess.run(cmd_json, capture_output=True, text=True, check=True)
        
        # 6. 读取并解析JSON结果
        recognized_texts = []
        print(f"读取OCR结果文件: {output_json_path}")
        with open(output_json_path, 'r') as f:
            ocr_result_data = json.load(f)
        
        # 解析OCR结果
        # OCR结果通常是一个列表，表示识别出的每一行文本框
        if isinstance(ocr_result_data, list):
            for page_res in ocr_result_data: # 可能有多页
                 if isinstance(page_res, list):
                    for line_res in page_res: # 每页中的每一行
                        # 每行的结果通常是 [box_info, (text, confidence)]
                        if len(line_res) >= 2 and isinstance(line_res[1], (list, tuple)) and len(line_res[1]) >= 2:
                             text = line_res[1][0]
                             if isinstance(text, str):
                                recognized_texts.append(text)
        
        # 合并所有识别出的文本
        full_text = " ".join(recognized_texts)

        print("OCR命令标准输出 (调试用):")
        print(result.stdout)
        if result.stderr:
            print("OCR命令标准错误输出 (调试用):")
            print(result.stderr)
            
        return full_text.strip()

    except requests.exceptions.RequestException as e:
        return f"下载图片失败: {str(e)}"
    except subprocess.CalledProcessError as e:
        error_msg = f"OCR命令执行失败 (退出码 {e.returncode})"
        if e.stdout:
            error_msg += f"\n标准输出: {e.stdout}"
        if e.stderr:
            error_msg += f"\n标准错误: {e.stderr}"
        return error_msg
    except json.JSONDecodeError as e:
        return f"解析OCR结果JSON失败: {str(e)}"
    except FileNotFoundError:
         return "错误: 未找到 'paddleocr' 命令。请确保已正确安装 'paddleocr' 包。"
    except Exception as e:
        return f"OCR识别失败 (未知错误): {str(e)}"
    finally:
        # 7. 清理临时文件
        if temp_image_path and os.path.exists(temp_image_path):
            try:
                os.remove(temp_image_path)
                print(f"已删除临时图片文件: {temp_image_path}")
            except OSError as e:
                print(f"删除临时图片文件失败: {e}")
        if 'output_json_path' in locals() and os.path.exists(output_json_path):
            try:
                os.remove(output_json_path)
                print(f"已删除临时OCR结果文件: {output_json_path}")
            except OSError as e:
                print(f"删除临时OCR结果文件失败: {e}")

# 目标图片URL
image_url = "https://www.stratesave.com/html/images/sidchgtrial.png"

# 识别并打印结果
print(f"正在从 {image_url} 识别图片...")
result_text = ocr_from_url(image_url)
print("\nOCR 识别结果:")
print(result_text)

# 检查识别结果是否是错误信息
if result_text.startswith("下载图片失败:") or result_text.startswith("OCR识别失败:") or result_text.startswith("错误:"):
    print("\n由于OCR识别失败，无法生成 getsid.bat。")
    sys.exit(1) # 以非零状态退出，表示脚本执行失败

# ----- 生成 getsid.bat 脚本 -----
# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 生成bat文件内容
bat_content = f'''@echo off
REM 脚本自动生成
REM 识别密钥: "{result_text}"

REM 切换到脚本所在目录
cd /D "%~dp0"

REM 检查 exe 文件是否存在
if not exist "sidchg64-3.0k.exe" (
    echo 错误: 未找到 sidchg64-3.0k.exe，请确保它与本脚本在同一目录下。
    pause
    exit /b 1
)

echo 找到 sidchg64-3.0k.exe，正在执行...
REM 执行命令，注意KEY值用双引号包裹
sidchg64-3.0k.exe /KEY="{result_text}" /F /R /OD /RESETALLAPPS

REM 检查上一条命令是否执行成功
if %errorlevel% neq 0 (
    echo 警告: sidchg64-3.0k.exe 执行可能未成功，退出码为 %errorlevel%
    pause
)

echo.
echo 脚本执行完成。
pause
'''

# 在脚本目录下生成getsid.bat文件
bat_path = os.path.join(script_dir, 'getsid.bat')
try:
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(bat_content)
    print(f"\n成功生成 getsid.bat 文件: {bat_path}")
    print("-" * 20 + " getsid.bat 预览 " + "-" * 20)
    print(bat_content)
    print("-" * 50)
except Exception as e:
    print(f"生成 getsid.bat 文件时发生错误: {str(e)}")
    sys.exit(1) # 以非零状态退出，表示脚本执行失败

