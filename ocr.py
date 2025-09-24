import requests
from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True # 允许加载截断的图片
from io import BytesIO
import os
# 导入 PaddleOCR，移除 draw_ocr
from paddleocr import PaddleOCR

def ocr_from_url_with_paddleocr(url):
    """
    从URL获取图片并使用PaddleOCR进行文本识别。
    返回识别出的纯文本字符串。
    """
    try:
        # 1. 下载图片 as bytes
        response = requests.get(url, timeout=30) # 添加超时
        response.raise_for_status()

        # 2. 使用PIL打开图片
        image_bytes = BytesIO(response.content)
        img_pil = Image.open(image_bytes)
        # 确保图片被加载到内存
        img_pil.load() 

        # 3. 初始化PaddleOCR
        # use_textline_orientation=True 替代已弃用的 use_angle_cls
        # lang='en' 指定识别语言为英语。
        # 注意：移除了导致错误的 show_log=False
        # verbose=False 可以减少一些非关键日志 (可选)
        ocr = PaddleOCR(use_textline_orientation=True, lang='en')#, verbose=False) # verbose可选

        # 4. 执行OCR识别
        # result 是一个列表，每个元素是一个识别出的文本块
        result = ocr.ocr(img_pil, cls=True) # cls=True 用于文本方向分类

        # 5. 提取纯文本
        recognized_texts = []
        # PaddleOCR 返回的结果结构可能因版本略有不同，这里做更健壮的判断
        # 通常 result 是一个列表，其第一个元素是所有检测到的文本框的列表
        if result is not None and len(result) > 0 and result[0] is not None:
            for line in result[0]: # 遍历每个检测到的文本行
                # 每个 line 是 [box_info, text_info]
                # box_info 是 [(x1,y1), (x2,y2), ...] 文本框坐标
                # text_info 是 [text_string, confidence_score]
                if len(line) > 1 and isinstance(line[1], list) and len(line[1]) > 1:
                    text = line[1][0]
                    if isinstance(text, str):
                        recognized_texts.append(text)
        
        # 将所有识别出的文本合并成一个字符串，用空格分隔
        full_text = " ".join(recognized_texts)
        
        return full_text.strip()
        
    except requests.exceptions.RequestException as e:
        return f"下载图片失败: {str(e)}"
    except Exception as e:
        # 打印更详细的错误信息以便调试
        import traceback
        error_details = traceback.format_exc()
        return f"OCR识别失败: {str(e)}\n详细错误信息:\n{error_details}"

# 目标图片URL
image_url = "https://www.stratesave.com/html/images/sidchgtrial.png"

# 识别并打印结果
print(f"正在从 {image_url} 识别图片...")
result_text = ocr_from_url_with_paddleocr(image_url)
print("\nOCR 识别结果:")
print(result_text)

# ----- 生成 getsid.bat 脚本 -----
# 检查识别结果是否是错误信息
if result_text.startswith("下载图片失败:") or result_text.startswith("OCR识别失败:"):
    print("\n由于识别失败，无法生成 getsid.bat。")
else:
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 生成bat文件内容
    bat_content = f'''@echo off
REM 脚本自动生成，基于PaddleOCR识别结果
REM 原始URL: {image_url}
REM 识别密钥: "{result_text}"

REM 切换到脚本所在目录，以确保 sidchg64-3.0k.exe 可被找到（如果它和bat文件在同目录）
cd /D %~dp0

REM 执行命令
REM 确保 sidchg64-3.0k.exe 存在且可用
REM 如果路径中包含空格，可能需要引号
if exist "sidchg64-3.0k.exe" (
    echo 找到 sidchg64-3.0k.exe，正在执行...
    "sidchg64-3.0k.exe" /KEY="{result_text}" /F /R /OD /RESETALLAPPS
) else (
    echo 错误: 未找到 sidchg64-3.0k.exe，请确保它与 getsid.bat 在同一目录下。
    pause
    exit /b 1
)'''

    # 在脚本目录下生成getsid.bat文件
    bat_path = os.path.join(script_dir, 'getsid.bat')
    try:
        with open(bat_path, 'w', encoding='utf-8') as f:
            f.write(bat_content)
        print(f"\n成功生成 getsid.bat 文件在: {bat_path}")
        print("-" * 30)
        print("getsid.bat 文件内容预览:")
        with open(bat_path, 'r', encoding='utf-8') as f:
            print(f.read())
        print("-" * 30)
    except Exception as e:
        print(f"生成 getsid.bat 文件时发生错误: {str(e)}")
