import os, requests, cv2, numpy as np
from PIL import Image
from io import BytesIO
import pytesseract
import easyocr

# --- 图片预处理函数 ---
def preprocess_image(image_url):
    resp = requests.get(image_url)
    img_array = np.asarray(bytearray(resp.content), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    # 转灰度
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 自适应二值化（比固定阈值更灵活）
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 15
    )
    # 中值滤波去噪
    denoised = cv2.medianBlur(thresh, 3)
    return denoised


def ocr_tesseract(img):
    """用tesseract识别，传入OpenCV格式"""
    pil_img = Image.fromarray(img)
    # psm 6 表示假设是单块文本，可用 7 表示单行文本
    config = "--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    text = pytesseract.image_to_string(pil_img, lang="eng", config=config)
    return text.strip()


def ocr_easyocr(img):
    """用easyocr识别，传OpenCV图像"""
    reader = easyocr.Reader(['en'], gpu=False)
    results = reader.readtext(img)
    # 拼接结果
    result_text = " ".join([res[1] for res in results])
    return result_text.strip()


def ocr_from_url(image_url):
    # Step1: 预处理
    preprocessed = preprocess_image(image_url)

    # Step2: 优先Tesseract
    result = ocr_tesseract(preprocessed)
    if result and len(result) > 2:
        print("Tesseract识别:", result)
        return result

    # Step3: Tesseract失败用EasyOCR
    result = ocr_easyocr(preprocessed)
    if result:
        print("EasyOCR识别:", result)
        return result

    return "未识别到有效文字"


if __name__ == "__main__":
    image_url = "https://www.stratesave.com/html/images/sidchgtrial.png"
    result = ocr_from_url(image_url)
    print("最终识别结果:", result)

    # 生成getsid.bat
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bat_content = f'''@echo off
cd %~dp0
sidchg64-3.0k.exe /KEY="{result}" /F /R /OD /RESETALLAPPS'''
    bat_path = os.path.join(script_dir, 'getsid.bat')
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(bat_content)

    print(f"已生成批处理文件: {bat_path}")
