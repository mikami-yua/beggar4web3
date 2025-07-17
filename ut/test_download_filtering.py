# test_download_filtering.py (v2 - 增加了日志过滤和下载测试)

import config
from source_acquirer2.baidupcs_client import BaiduPCSClient
from manager.log_handler import read_processed_files


def run_download_test():
    """
    测试从“发现文件列表”到“过滤已下载”再到“执行下载”的完整流程。
    """
    print("=" * 60)
    print("=  启动 BaiduPCS-Go 客户端单元测试：增量下载  =")
    print("=" * 60)

    # --- 模拟：我们已经通过智能发现获取到的文件列表 ---
    # (这里我们硬编码一个列表来模拟 get_recent_report_filenames 的返回结果)
    discovered_files = [
        "2025-07-03-JPM-Cable, Satellite, and Telecom Services Spectrum of Opportunity Ranking Cable, Satellite....pdf",
        "2025-07-07-JPM-Cryptocurrency Markets July 1 Spot ETP Flows ETH Sales Remain Positive($41 mn)....pdf",
        "2025-07-13-JPM-US 2Q GDP revised to 3.0 pct on softer consumer spending.pdf"
    ]
    print(f"[*] [模拟] 假设我们已从网盘发现 {len(discovered_files)} 个近期文件。")

    # --- 步骤一：从日志中读取已处理过的文件 ---
    print("\n--- [1/3] 正在读取下载日志 ---")
    log_path = config.MANAGER_CONFIG.get("processed_log_path")
    processed_files = read_processed_files(log_path)

    # --- 步骤二：找出需要下载的新文件 (差集运算) ---
    print("\n--- [2/3] 正在过滤已下载的文件 ---")
    files_to_download = [f for f in discovered_files if f not in processed_files]

    if not files_to_download:
        print("✅ 过滤完成：所有发现的文件都已处理过，无需下载。")
        print("\n--- 测试成功结束 ---")
        return
    else:
        print(f"[*] 过滤完成：发现 {len(files_to_download)} 个新文件需要下载:")
        for f in files_to_download:
            print(f"    -> {f}")

    # --- 步骤三：执行下载命令 ---
    print("\n--- [3/3] 正在调用下载命令 ---")
    client = BaiduPCSClient()
    save_directory = config.PATH_CONFIG.get("PDF_SOURCE_DIR")

    # 为了测试，我们需要先切换到包含这些文件的目录
    # 注意：在真实流程中，这个cd操作应该在获取discovered_files之前完成
    base_reports_path = "/ai-agent-input-data/2025年摩根大通研报/2025/7月"  # 假设文件都在7月目录
    client.change_remote_directory(base_reports_path)

    download_success = client.download_files(files_to_download, save_directory)

    print("\n--- 最终测试结果 ---")
    if download_success:
        print("✅✅✅ 测试成功！下载命令已成功执行。")
    else:
        print("❌❌❌ 测试失败。下载命令执行失败，请检查上面的日志。")


if __name__ == "__main__":
    # 运行测试前，请确保您已经在 /home/pdf-data/downloaded.log 文件中
    # 放入了一两个上面 discovered_files 列表里的文件名，用于验证过滤功能
    print("[!] 测试准备: 请确保您已在 config.py 中配置的日志路径下创建了 downloaded.log 文件")
    print("    并可以手动在其中放入一些文件名来测试过滤功能。")
    input("准备好后，请按 Enter键 继续...")
    run_download_test()