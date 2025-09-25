import os
import requests
from PIL import Image
import pytesseract
import tempfile

# 配置 Tesseract 路径（Windows 用户需指定，Linux/macOS 通常无需设置）
# 如果你已将 Tesseract 添加到系统 PATH，可忽略此行。
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def ocr_from_url(image_url):
    """
    从网络图片 URL 下载图片并 OCR 识别文字
    """
    try:
        print(f"正在下载图片: {image_url}")
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()

        # 使用临时文件避免写入磁盘（可选）
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_file.write(response.content)
            tmp_path = tmp_file.name

        # 打开图片并 OCR 识别
        print("正在识别图片文字...")
        image = Image.open(tmp_path)
        # 可选：预处理图片提高识别率（灰度、二值化）
        image = image.convert('L')  # 转为灰度
        text = pytesseract.image_to_string(image, lang='eng').strip()

        # 清理临时文件
        os.unlink(tmp_path)

        if not text:
            print("⚠️ 识别结果为空，请检查图片清晰度或文字颜色。")
        else:
            print(f"✅ 识别成功: {text}")

        return text

    except Exception as e:
        print(f"❌ OCR 失败: {e}")
        return ""

def generate_bat_script(result, script_dir=None):
    """
    生成 getsid.bat 脚本，使用识别出的密钥
    """
    if script_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))

    bat_content = f'''@echo off
cd %~dp0
sidchg64-3.0k.exe /KEY="{result}" /F /R /OD /RESETALLAPPS
pause
'''

    bat_path = os.path.join(script_dir, 'getsid.bat')

    try:
        with open(bat_path, 'w', encoding='utf-8') as f:
            f.write(bat_content)
        print(f"✅ .bat 文件已生成: {bat_path}")
        return bat_path
    except Exception as e:
        print(f"❌ 生成 .bat 文件失败: {e}")
        return None

# ========== 主程序 ==========
if __name__ == "__main__":
    image_url = "https://www.stratesave.com/html/images/sidchgtrial.png"

    # 1. OCR 识别图片
    result = ocr_from_url(image_url)

    if not result:
        print("❌ 未识别到有效文本，脚本终止。")
        exit(1)

    print("\n" + "="*50)
    print("识别结果（赋值给result变量）:")
    print(result)
    print("="*50 + "\n")

    # 2. 生成 .bat 文件
    generate_bat_script(result)

    print("\n🎉 操作完成！请在脚本所在目录检查 getsid.bat 文件。")
