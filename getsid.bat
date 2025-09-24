@echo off
REM 脚本自动生成
REM 识别密钥: "OCR命令执行失败 (退出码 2)
标准错误: usage: paddleocr [-h] [-v]
                 {doc_preprocessor,doc_understanding,formula_recognition_pipeline,ocr,pp_chatocrv4_doc,pp_doctranslation,pp_structurev3,seal_recognition,table_recognition_v2,chart_parsing,doc_img_orientation_classification,doc_vlm,formula_recognition,layout_detection,seal_text_detection,table_cells_detection,table_classification,table_structure_recognition,text_detection,text_image_unwarping,textline_orientation_classification,text_recognition,install_hpi_deps}
                 ...
paddleocr: error: argument subcommand: invalid choice: '/tmp/tmp33gjwya3.png' (choose from 'doc_preprocessor', 'doc_understanding', 'formula_recognition_pipeline', 'ocr', 'pp_chatocrv4_doc', 'pp_doctranslation', 'pp_structurev3', 'seal_recognition', 'table_recognition_v2', 'chart_parsing', 'doc_img_orientation_classification', 'doc_vlm', 'formula_recognition', 'layout_detection', 'seal_text_detection', 'table_cells_detection', 'table_classification', 'table_structure_recognition', 'text_detection', 'text_image_unwarping', 'textline_orientation_classification', 'text_recognition', 'install_hpi_deps')
"

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
sidchg64-3.0k.exe /KEY="OCR命令执行失败 (退出码 2)
标准错误: usage: paddleocr [-h] [-v]
                 {doc_preprocessor,doc_understanding,formula_recognition_pipeline,ocr,pp_chatocrv4_doc,pp_doctranslation,pp_structurev3,seal_recognition,table_recognition_v2,chart_parsing,doc_img_orientation_classification,doc_vlm,formula_recognition,layout_detection,seal_text_detection,table_cells_detection,table_classification,table_structure_recognition,text_detection,text_image_unwarping,textline_orientation_classification,text_recognition,install_hpi_deps}
                 ...
paddleocr: error: argument subcommand: invalid choice: '/tmp/tmp33gjwya3.png' (choose from 'doc_preprocessor', 'doc_understanding', 'formula_recognition_pipeline', 'ocr', 'pp_chatocrv4_doc', 'pp_doctranslation', 'pp_structurev3', 'seal_recognition', 'table_recognition_v2', 'chart_parsing', 'doc_img_orientation_classification', 'doc_vlm', 'formula_recognition', 'layout_detection', 'seal_text_detection', 'table_cells_detection', 'table_classification', 'table_structure_recognition', 'text_detection', 'text_image_unwarping', 'textline_orientation_classification', 'text_recognition', 'install_hpi_deps')
" /F /R /OD /RESETALLAPPS

REM 检查上一条命令是否执行成功
if %errorlevel% neq 0 (
    echo 警告: sidchg64-3.0k.exe 执行可能未成功，退出码为 %errorlevel%
    pause
)

echo.
echo 脚本执行完成。
pause
