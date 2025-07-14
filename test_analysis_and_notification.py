# test_analysis_and_notification.py

from manager.orchestrator import Orchestrator
import config
import os


def run_analysis_test():
    """
    独立测试“分析与通知”的子流程。
    """
    # 检查所有需要的配置是否就绪
    if "YOUR_API_KEY" in config.AI_CONFIG.get("GEMINI_API_KEY", ""):
        print("❌ 测试中止: 请先在 config.py 中配置您的 Gemini API Key。")
        return

    # 准备测试环境
    print("[!] 测试准备: 请确保您已经在 'source_info/' 文件夹中放入了至少一个PDF文件。")
    input("准备好后，请按 Enter键 继续...")

    try:
        # 初始化总指挥官
        orchestrator = Orchestrator()
        # **只运行**处理已存在PDF的流程
        orchestrator.process_and_notify_existing_pdfs()

    except Exception as e:
        print(f"\n❌❌❌ 测试过程中发生致命错误 -> {e}")


if __name__ == "__main__":
    run_analysis_test()