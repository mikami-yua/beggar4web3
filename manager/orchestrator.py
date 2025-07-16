# manager/orchestrator.py (这是正确的、调用现有模块的版本)

import os
import time
import config
import json
from source_acquirer2.baidupcs_client import BaiduPCSClient

# --- 导入我们已有的模块化组件 ---
from analysis_note.core_analyzer import analyze_document
# 根据您最终的选择，从notifier模块导入对应的发送函数
from notifier.email_sender import send_analysis_report
from .log_handler import read_processed_files, log_processed_file


class Orchestrator:
    # ... __init__ 函数保持不变 ...
    def __init__(self):
        self.baidu_client = BaiduPCSClient()
        self.log_path = config.MANAGER_CONFIG.get("processed_log_path")
        self.local_download_dir = config.PATH_CONFIG.get("PDF_SOURCE_DIR")
        self.output_dir = config.PATH_CONFIG.get("ANALYSIS_OUTPUT_DIR")
        self.gemini_api_key = config.AI_CONFIG.get("GEMINI_API_KEY")

        # 在启动时，确保所有需要的本地目录都存在
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

    def run_full_pipeline(self):
        """
        执行从“获取->下载->记录->分析->通知”的完整流水线。
        """
        print("=" * 60)
        print("=  启动全自动研报分析Agent  =")
        print("=" * 60)

        # --- 阶段一：发现需要处理的新文件 ---
        print("\n[1/5] 正在发现新文件...")

        # 1. 从日志文件中加载已处理过的文件列表
        processed_files_set = read_processed_files(self.log_path)

        # 2. 从网盘上获取近期的所有研报文件名
        base_path = config.BAIDUPCS_CONFIG.get("remote_reports_path_base")
        remote_files_list = self.baidu_client.get_recent_report_filenames(base_path, days=10)

        if remote_files_list is None:
            print("❌ 流程中止: 无法从网盘获取文件列表。")
            return

        # 3. 计算出真正需要下载的新文件（增量部分）
        files_to_process = [f for f in remote_files_list if f not in processed_files_set]

        if not files_to_process:
            print("[*] 所有近期文件均已处理完毕，本次无新任务，流程结束。")
            return

        print(f"\n[*] 发现 {len(files_to_process)} 个新文件需要处理，开始逐条执行...")
        print("-" * 60)

        # --- 阶段二至五：逐一处理新文件 ---
        for filename in files_to_process:
            print(f"\n>>> 开始处理新报告: {filename}")

            local_pdf_path = os.path.join(self.local_download_dir, filename)
            json_output_path = os.path.join(self.output_dir, f"{os.path.splitext(filename)[0]}.json")

            # 2. 下载文件
            print("\n[2/5] 正在下载文件...")
            if not self.baidu_client.download_files([filename], self.local_download_dir):
                print(f"[-] 下载失败，跳过文件: {filename}")
                continue

            # 3. 下载成功后，立刻将文件名写入日志
            print("\n[3/5] 正在更新处理日志...")
            log_processed_file(self.log_path, filename)

            # 4. AI分析
            print("\n[4/5] 正在进行AI分析...")
            analysis_result = analyze_document(local_pdf_path, self.gemini_api_key)

            if not analysis_result:
                print(f"[-] AI分析失败，跳过文件: {filename}")
                if os.path.exists(local_pdf_path):
                    os.remove(local_pdf_path)
                continue

            with open(json_output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=4)
            print(f"[+] 分析结果已保存至: {json_output_path}")

            # 5. 发送通知
            print("\n[5/5] 正在发送邮件通知...")
            # 注意：这里的邮件发送函数需要根据您最终的选择来确定
            # 我们假设最终使用SendGrid API，并且需要一个适配过的formatter
            # 为了简化，我们暂时只传递分析结果和文件名
            send_analysis_report(analysis_result, {"title": filename})

            # 清理本次下载的源文件，节省服务器空间
            if os.path.exists(local_pdf_path):
                os.remove(local_pdf_path)
            print("[*] 临时PDF文件已清理。")
            print(f">>> 报告处理完成: {filename}")
            print("-" * 60)
            time.sleep(10)  # 礼貌性停顿，避免请求过于频繁

        print("\n✅ 所有新文件处理完毕，流程结束。")
