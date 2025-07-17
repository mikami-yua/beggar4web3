# test_log_then_download.py

import config
from source_acquirer2.baidupcs_client import BaiduPCSClient
from manager.log_handler import read_processed_files, log_processed_file


def run_log_then_download_test():
    """
    独立测试“先记录，后下载”的完整增量逻辑。
    """
    print("=" * 60)
    print("=  启动单元测试：先记录日志，后执行下载  =")
    print("=" * 60)

    try:
        client = BaiduPCSClient()
        log_path = config.MANAGER_CONFIG.get("processed_log_path")

        # --- 步骤一：发现所有近期文件 ---
        print("\n--- [1/4] 正在从网盘获取近期文件列表 ---")
        base_reports_path = config.BAIDUPCS_CONFIG.get("remote_reports_path_base")
        all_recent_files = client.get_recent_report_filenames(base_reports_path, days=10)

        if all_recent_files is None:
            print("❌ 测试中止: 从网盘获取文件列表失败。")
            return

        # --- 步骤二：读取日志，决策出新文件列表 ---
        print("\n--- [2/4] 正在读取日志并过滤新文件 ---")
        processed_files = read_processed_files(log_path)
        files_to_process = [f for f in all_recent_files if f not in processed_files]

        if not files_to_process:
            print("✅ 过滤完成：所有发现的文件都已处理过，无需任何操作。")
            print("\n--- 测试成功结束 ---")
            return

        print(f"[*] 过滤完成：决策出 {len(files_to_process)} 个新文件需要处理:")
        for f in files_to_process:
            print(f"    -> {f}")

        # --- 步骤三 (核心改动)：立刻将所有新文件名写入日志 ---
        print("\n--- [3/4] 正在将新文件列表预先写入日志 ---")
        for filename in files_to_process:
            # 调用我们已经写好的日志记录函数
            log_processed_file(log_path, filename)

        print("✅ 日志记录完毕。")

        # --- 步骤四：执行下载命令 ---
        print("\n--- [4/4] 正在调用下载命令 ---")
        save_directory = config.PATH_CONFIG.get("PDF_SOURCE_DIR")

        # 为了测试，需要先切换到包含这些文件的目录
        # 注意：在真实流程中，这个cd操作已包含在get_recent_report_filenames内部
        # 我们在这里再执行一次以确保当前工作目录正确
        # (真实流程中可以优化掉这一步)
        client.change_remote_directory(f"{base_reports_path}/{config.CURRENT_TEST_YEAR}/{config.CURRENT_TEST_MONTH}月/")

        download_success = client.download_files(files_to_process, save_directory)

        print("\n--- 最终测试结果 ---")
        if download_success:
            print("✅✅✅ 测试成功！下载命令已成功执行。")
        else:
            print("❌❌❌ 测试失败。下载命令执行失败，请检查上面的日志。")

    except (ValueError, RuntimeError) as e:
        print(f"\n❌❌❌ 测试中止: 发生致命错误 -> {e}")
        print("   请检查您的 config.py 文件或 BaiduPCS-Go 工具本身。")


# 为了方便测试，我们在config中临时加入年月信息
def add_test_config():
    import datetime
    now = datetime.datetime.now()
    config.CURRENT_TEST_YEAR = now.year
    config.CURRENT_TEST_MONTH = now.month


if __name__ == "__main__":
    print("[!] 测试准备: 请确保您已在 config.py 中配置的日志路径下创建了 downloaded.log 文件")
    print("    并可以手动清空或在其中放入一些文件名来测试。")
    input("准备好后，请按 Enter键 继续...")

    # 临时向config模块添加动态的年月信息
    add_test_config()

    run_log_then_download_test()