# manager/orchestrator.py (这是正确的、调用现有模块的版本)

import os
import time
import config
import json

# --- 导入我们已有的模块化组件 ---
from analysis_note.core_analyzer import analyze_document
# 根据您最终的选择，从notifier模块导入对应的发送函数
from notifier.email_sender import send_analysis_report


class Orchestrator:
    # ... __init__ 函数保持不变 ...
    def __init__(self):
        self.local_download_dir = config.PATH_CONFIG.get("PDF_SOURCE_DIR")
        self.output_dir = config.PATH_CONFIG.get("ANALYSIS_OUTPUT_DIR")
        self.gemini_api_key = config.AI_CONFIG.get("GEMINI_API_KEY")
        os.makedirs(self.local_download_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def process_and_notify_existing_pdfs(self):
        """
        一个独立的流程，用于处理在source_info文件夹中已存在的所有PDF文件。
        它会调度分析模块和通知模块。
        """
        print("=" * 60)
        print("=  启动“分析与通知”测试流程  =")
        print("=" * 60)

        pdf_files = [f for f in os.listdir(self.local_download_dir) if f.lower().endswith('.pdf')]
        if not pdf_files:
            print(f"[*] 目录 '{self.local_download_dir}' 中没有找到需要分析的PDF文件。")
            return

        print(f"[*] 发现 {len(pdf_files)} 个PDF文件，开始逐一处理...")
        print("-" * 60)

        for filename in pdf_files:
            print(f"\n>>> 开始处理文件: {filename}")
            local_pdf_path = os.path.join(self.local_download_dir, filename)
            json_output_path = os.path.join(self.output_dir, f"{os.path.splitext(filename)[0]}.json")

            # 步骤 a: 调用 analysis_note 模块
            print("\n[1/2] 正在进行AI分析...")
            analysis_result = analyze_document(local_pdf_path, self.gemini_api_key)

            if not analysis_result:
                print(f"[-] AI分析失败，跳过文件: {filename}")
                continue

            with open(json_output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=4)
            print(f"[+] 分析结果已保存至: {json_output_path}")

            # 步骤 b: 调用 notifier 模块
            print("\n[2/2] 正在发送邮件通知...")
            send_analysis_report(analysis_result, filename)

            print(f">>> 文件处理完成: {filename}")
            print("-" * 60)
            time.sleep(5)

        print("\n✅ 所有已存在的PDF文件处理完毕。")
