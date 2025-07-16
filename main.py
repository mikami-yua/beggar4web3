# main.py (最终版 - 带内置定时器)

import time
import os
import config
from manager.orchestrator import Orchestrator


def main():
    """
    项目的主入口函数，包含一个无限循环，以实现定时任务。
    """
    # --- 启动前的配置检查 (保持不变) ---
    print("--- 正在准备启动AI Agent ---")
    try:
        if "YOUR_API_KEY" in config.AI_CONFIG.get("GEMINI_API_KEY", ""):
            print("❌ 启动失败: Gemini API Key尚未在config.py中配置。")
            return
        if not os.path.exists(config.BAIDUPCS_CONFIG.get("executable_path", "")):
            print("❌ 启动失败: BaiduPCS-Go的路径在config.py中配置不正确或文件不存在。")
            return
    except Exception as e:
        print(f"❌ 启动失败: 读取配置文件时发生错误 -> {e}")
        return

    print("[*] 配置检查通过，Agent准备就绪。")

    # --- vvv 这里是核心改动：无限循环 vvv ---
    while True:
        try:
            # 1. 初始化总指挥官
            orchestrator = Orchestrator()

            # 2. 运行完整的工作流
            orchestrator.run_full_pipeline()

        except Exception as e:
            # 捕获任何在运行时可能发生的致命错误
            print(f"\n❌❌❌ 在本次运行周期中发生致命错误: {e}")
            print("   将等待下一个周期再试。")

        # 3. 完成一次循环后，进入休眠
        sleep_hours = 4
        sleep_seconds = sleep_hours * 60 * 60
        print("\n============================================================")
        print(f"=== 本次任务周期已完成，系统将休眠 {sleep_hours} 小时。===")
        print(
            f"=== 下次运行时间: {(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + sleep_seconds)))} ===")
        print("============================================================")

        try:
            time.sleep(sleep_seconds)
        except KeyboardInterrupt:
            # 允许用户通过 Ctrl+C 来优雅地退出程序
            print("\n\n[*] 检测到手动中断(Ctrl+C)，AI Agent正在关闭。再见！")
            break  # 跳出 while True 循环
    # --- ^^^ 这里是核心改动 ^^^ ---


if __name__ == "__main__":
    main()