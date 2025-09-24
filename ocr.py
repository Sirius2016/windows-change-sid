import requests
from PIL import Image
from io import BytesIO
import os
# 导入 PaddleOCR，移除 draw_ocr，因为它导致了 ImportError
from paddleocr import PaddleOCR

def ocr_from_url_with_paddleocr(url):
    """
    从URL获取图片并使用PaddleOCR进行文本识别。
    返回识别出的纯文本字符串。
    """
    try:
        # 1. 下载图片 as bytes
        response = requests.get(url)
        response.raise_for_status() # 检查请求是否成功

        # 2. 使用PIL打开图片
        image_bytes = BytesIO(response.content)
        img_pil = Image.open(image_bytes)

        # 3. 初始化PaddleOCR
        # use_angle_cls=True 表示会进行文本方向分类，这通常会提高识别率
        # lang='en' 指定识别语言为英语。如果图片包含中文或其他语言，需要相应修改。
        # 如果需要多语言识别，例如中英文混合，可以设置为 lang='ch,en'
        # show_log=False 可以关闭 PaddleOCR 的默认日志输出
        ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)

        # 4. 执行OCR识别
        # result 是一个列表，每个元素是一个识别出的文本块，包含 bbox 和 text
        # 例如: [[(x1, y1), (x2, y2), ...], ['识别出的文本', confidence_score]]
        result = ocr.ocr(img_pil, cls=True)

        # 5. 提取纯文本
        recognized_texts = []
        if result and result[0]: # 确保result不是None或空列表
            for res in result[0]: # result[0] 包含所有识别结果
                if len(res) > 1 and isinstance(res[1], list) and len(res[1]) > 0:
                    # res[1] 是一个列表, 包含 [text, confidence]
                    text = res[1][0]
                    recognized_texts.append(text)
        
        # 将所有识别出的文本合并成一个字符串，用空格分隔
        full_text = " ".join(recognized_texts)
        
        return full_text.strip()
        
    except requests.exceptions.RequestException as e:
        return f"下载图片失败: {str(e)}"
    except Exception as e:
        return f"OCR识别失败: {str(e)}"

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
cd %~dp0

REM 执行命令
REM 确保 sidchg64-3.0k.exe 存在且可用
sidchg64-3.0k.exe /KEY="{result_text}" /F /R /OD /RESETALLAPPS'''

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

