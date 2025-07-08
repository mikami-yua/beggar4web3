# main.py

import os
import json
import config
from analysis_note.core_analyzer import analyze_document


def setup_proxy():
    """
    从配置文件读取代理设置并应用到环境变量。
    """
    if config.PROXY_CONFIG.get("enabled", False):
        proxy_address = config.PROXY_CONFIG.get("address")
        if proxy_address:
            os.environ['http_proxy'] = proxy_address
            os.environ['https_proxy'] = proxy_address
            os.environ['HTTP_PROXY'] = proxy_address
            os.environ['HTTPS_PROXY'] = proxy_address
            print(f"[*] 代理已通过配置文件启用: {proxy_address}")
        else:
            print("[!] 代理配置已启用，但未提供地址。")
    else:
        print("[*] 未启用代理配置。")


def process_all_files():
    """
    处理源文件夹下的所有PDF文件。
    """
    # 检查关键配置是否存在等代码保持不变...
    api_key = config.AI_CONFIG.get("GEMINI_API_KEY")
    source_dir = config.PATH_CONFIG.get("PDF_SOURCE_DIR")
    output_dir = config.PATH_CONFIG.get("ANALYSIS_OUTPUT_DIR")

    if not api_key or "xxxxxxx" in api_key:
        print("[!] 错误: Gemini API密钥未在config.py的AI_CONFIG中正确配置。")
        return

    if not source_dir or not output_dir:
        print("[!] 错误: 路径配置未在config.py的PATH_CONFIG中正确设置。")
        return

    os.makedirs(output_dir, exist_ok=True)

    print("--- 启动新闻分析代理 ---")

    files_in_source = os.listdir(source_dir)
    if not files_in_source:
        print(f"[*] 源目录 '{source_dir}' 为空，未找到待分析文件。")

    for filename in files_in_source:
        # ... 核心循环逻辑保持不变 ...
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(source_dir, filename)
            output_filename = os.path.splitext(filename)[0] + ".json"
            output_path = os.path.join(output_dir, output_filename)

            if os.path.exists(output_path):
                print(f"[*] 跳过: {filename} 的分析结果已存在。")
                continue

            result = analyze_document(pdf_path, api_key)

            if result:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)
                print(f"[+] 成功: {filename} 的分析已保存至 {output_path}")
            else:
                print(f"[-] 失败: 未能成功分析 {filename}。")
        print("-" * 20)

    print("--- 分析流程结束 ---")


if __name__ == "__main__":
    # 在执行任何操作之前，首先设置代理
    setup_proxy()

    # 然后运行主流程
    process_all_files()