# analysis_note/core_analyzer.py

import google.generativeai as genai
import json
import time
import config  # 导入config来获取模型名称
from .prompt_manager import get_news_analysis_prompt


# 不再需要 from .utils import extract_text_from_pdf

def analyze_document(pdf_path: str, api_key: str) -> dict | None:
    """
    使用File API对单个PDF文档执行完整的多模态分析。
    """
    print(f"[*] Analyzing document with File API: {pdf_path}")

    try:
        # --- 1. 配置Gemini ---
        genai.configure(api_key=api_key)
        model_name = config.AI_CONFIG.get("MODEL_NAME", "gemini-1.5-pro-latest")

        # --- 2. 上传文件 ---
        print(f"[*] Uploading {pdf_path} to Google...")
        # display_name是可选的，方便你在文件列表中识别
        uploaded_file = genai.upload_file(path=pdf_path, display_name=pdf_path)
        print(f"[*] Completed upload. File name: {uploaded_file.name}")

        # --- 3. 准备Prompt和模型 ---
        # prompt不再需要传入文章内容
        prompt = get_news_analysis_prompt()
        model = genai.GenerativeModel(model_name)

        # --- 4. 发送包含文件引用的请求 ---
        print("[*] Sending request with file reference to AI...")
        # 将上传的文件对象和prompt一起发送
        response = model.generate_content([uploaded_file, prompt])

        # --- 5. 清理和解析返回的JSON数据 ---
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        analysis_result = json.loads(cleaned_response)
        print(f"[+] Successfully parsed AI response.")

        # --- 6. (可选但推荐) 删除已上传的文件 ---
        # 文件在Google服务器上会保留48小时，如果不再需要可以主动删除
        print(f"[*] Deleting uploaded file: {uploaded_file.name}")
        genai.delete_file(uploaded_file.name)

        return analysis_result

    except Exception as e:
        print(f"[!] An error occurred during multimodal analysis for {pdf_path}: {e}")
        # 如果出错，检查response对象是否存在，以便打印原始返回信息
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"[!] Raw response from AI: {response.text}")
        return None