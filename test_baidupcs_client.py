# test_baidupcs_client.py (v2 - 增加了cd测试步骤)

import config
from source_acquirer2.baidupcs_client import BaiduPCSClient


def run_clear_directory_test():
    """
    测试先切换到根目录，然后再清空指定目录的功能。
    """
    print("=" * 60)
    print("=  启动 BaiduPCS-Go 客户端单元测试 (切换并清空)  =")
    print("=" * 60)

    # 依然使用一个安全的测试目录
    target_dir_to_clear = "/ai-agent-input-data/"

    print(f"[*] 本次测试将首先切换到根目录 '/'，然后尝试清空: {target_dir_to_clear}")
    input("准备好后，请按 Enter键 继续...")

    try:
        client = BaiduPCSClient()

        # --- 步骤一：先切换到根目录 ---
        print("\n--- [1/2] 正在执行目录切换 (cd /) ---")
        cd_success = client.change_remote_directory("/")
        if not cd_success:
            print("\n❌❌❌ 测试中止: 切换到根目录失败，后续操作无法进行。")
            return

        # --- 步骤二：再执行清空操作 ---
        print("\n--- [2/2] 正在执行清空目录操作 ---")
        clear_success = client.clear_remote_directory(target_dir_to_clear)

        print("\n--- 最终测试结果 ---")
        if clear_success:
            print(f"✅✅✅ 测试成功！函数返回了True，表示目录 '{target_dir_to_clear}' 已被成功清空。")
        else:
            print(f"❌❌❌ 测试失败。函数返回了False，请检查上面的日志以定位问题。")

    except (ValueError, RuntimeError) as e:
        print(f"\n❌❌❌ 测试中止: 发生致命错误 -> {e}")
        print("   请检查您的 config.py 文件或 BaiduPCS-Go 工具本身。")


def run_transfer_test():
    """
    测试先切换到指定目录，然后转存一个分享链接的功能。
    """
    print("=" * 60)
    print("=  启动 BaiduPCS-Go 客户端单元测试：转存分享文件  =")
    print("=" * 60)

    # --- 测试用的配置 ---
    # 1. 我们要把文件转存到哪个目录
    target_dir = "/ai-agent-input-data/"

    # 2. 我们要转存的分享链接和密码
    share_link = "https://pan.baidu.com/s/1wvtGTGzx0No3xGDcSdvj5Q?pwd=6666"
    password = "6666"  # 即使链接里有pwd，也保留密码变量以便函数调用

    print(f"[*] 本次测试的目标:")
    print(f"    1. 切换到网盘目录: {target_dir}")
    print(f"    2. 转存链接: {share_link}")
    input("准备好后，请按 Enter键 继续...")

    try:
        client = BaiduPCSClient()

        # --- 步骤一：切换到目标目录 ---
        print("\n--- [1/2] 正在执行目录切换 ---")
        cd_success = client.change_remote_directory(target_dir)
        if not cd_success:
            print("\n❌❌❌ 测试中止: 切换到目标目录失败，后续操作无法进行。")
            return

        # --- 步骤二：执行转存操作 ---
        print("\n--- [2/2] 正在执行转存操作 ---")
        transfer_success = client.transfer_shared_link(share_link, password)

        print("\n--- 最终测试结果 ---")
        if transfer_success:
            print(f"✅✅✅ 测试成功！函数返回了True，表示分享链接已成功转存到 '{target_dir}'。")
        else:
            print(f"❌❌❌ 测试失败。函数返回了False，请检查上面的日志以定位问题。")

    except (ValueError, RuntimeError) as e:
        print(f"\n❌❌❌ 测试中止: 发生致命错误 -> {e}")
        print("   请检查您的 config.py 文件或 BaiduPCS-Go 工具本身。")


def run_filtering_test():
    """
    测试智能发现并按日期过滤文件的功能。
    """
    print("=" * 60)
    print("=  启动 BaiduPCS-Go 客户端单元测试：智能文件过滤  =")
    print("=" * 60)

    # --- 测试用的配置 ---
    # 这是研报存放的根目录，程序会自动在此基础上拼接年月
    base_reports_path = "/ai-agent-input-data/2025年摩根大通研报"

    # 我们要筛选最近多少天的报告
    days_to_filter = 10

    print(f"[*] 本次测试的目标:")
    print(f"    1. 智能查找目录: {base_reports_path}/<自动计算的年月>/")
    print(f"    2. 筛选出最近 {days_to_filter} 天的报告")
    input("准备好后，请按 Enter键 继续...")

    try:
        client = BaiduPCSClient()

        # 执行我们新的核心功能
        recent_files = client.get_recent_report_filenames(base_reports_path, days=days_to_filter)

        print("\n--- 最终测试结果 ---")
        if recent_files:
            print(f"✅✅✅ 测试成功！筛选出的文件列表如下:")
            for i, filename in enumerate(recent_files, 1):
                print(f"   {i}. {filename}")
        else:
            print(f"⚠️⚠️⚠️ 测试完成，但未筛选到任何符合条件的文件。")
            print("   这可能是正常的（如果确实没有近期文件），也可能说明过滤逻辑需要检查。")

    except (ValueError, RuntimeError) as e:
        print(f"\n❌❌❌ 测试中止: 发生致命错误 -> {e}")
        print("   请检查您的 config.py 文件或 BaiduPCS-Go 工具本身。")


if __name__ == "__main__":
    run_filtering_test()