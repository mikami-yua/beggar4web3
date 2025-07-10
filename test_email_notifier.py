# test_notifier.py

import os
import json
import config
from notifier.formatters import format_analysis_for_email
from notifier.email_sender import send_analysis_report


def load_latest_analysis_json(output_dir: str) -> tuple[dict | None, str | None]:
    """
    从输出目录加载最新的一个JSON分析文件。
    :param output_dir: 包含JSON文件的目录路径。
    :return: 一个包含 (json数据字典, 文件名) 的元组，如果找不到文件则返回 (None, None)。
    """
    print(f"[*] 正在扫描目录 '{output_dir}' 以查找最新的分析文件...")

    # 检查目录是否存在
    if not os.path.exists(output_dir):
        print(f"[!] 错误: 输出目录 '{output_dir}' 不存在。")
        return None, None

    # 筛选出所有的 .json 文件
    json_files = [f for f in os.listdir(output_dir) if f.lower().endswith(".json")]

    if not json_files:
        print(f"[!] 错误: 在 '{output_dir}' 中未找到任何 .json 文件。")
        return None, None

    # 找到最新的文件
    full_paths = [os.path.join(output_dir, f) for f in json_files]
    latest_file_path = max(full_paths, key=os.path.getmtime)
    latest_filename = os.path.basename(latest_file_path)

    print(f"[*] 已找到最新的分析文件: {latest_filename}")

    # 加载并返回JSON内容
    try:
        with open(latest_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # 将原始PDF文件名（不含.json后缀）传递出去
        source_pdf_filename = os.path.splitext(latest_filename)[0] + ".pdf"
        return data, source_pdf_filename
    except (json.JSONDecodeError, IOError) as e:
        print(f"[!] 错误: 读取或解析文件 '{latest_filename}' 时失败: {e}")
        return None, None


def test_formatter(analysis_data: dict, source_filename: str):
    """
    单元测试：仅测试JSON到邮件文本的格式化功能。
    """
    print("\n--- 1. 正在测试邮件内容格式化功能 ---")

    subject, body = format_analysis_for_email(analysis_data, source_filename)

    print("\n[生成的邮件主题]:")
    print(subject)

    print("\n[生成的邮件正文]:")
    print("-" * 40)
    print(body)
    print("-" * 40)

    print("\n✅ 格式化功能测试完成。请检查以上输出是否符合预期。")


def test_email_sender(analysis_data: dict, source_filename: str):
    """
    集成测试：测试完整的邮件发送功能。
    """
    print("\n--- 2. 正在测试邮件发送功能 ---")
    print("!! 警告: 即将使用真实数据发送一封测试邮件... !!")

    send_analysis_report(analysis_data, source_filename)


if __name__ == "__main__":
    print("=" * 50)
    print("=  启动 Notifier 模块单元测试 (使用真实数据)  =")
    print("=" * 50)

    # 在开始前，检查邮件配置
    if not hasattr(config, 'EMAIL_CONFIG') or not config.EMAIL_CONFIG.get("use_email"):
        print("\n❌ 测试中止: 邮件功能在 config.py 中被禁用或未配置。")
    else:
        # --- 核心改动：从文件加载数据，而不是使用模拟数据 ---
        output_directory = config.PATH_CONFIG.get("ANALYSIS_OUTPUT_DIR")
        real_analysis_data, real_filename = load_latest_analysis_json(output_directory)

        if real_analysis_data and real_filename:
            # 如果成功加载数据，则用这份真实数据执行测试
            test_formatter(real_analysis_data, real_filename)
            test_email_sender(real_analysis_data, real_filename)
            print("\n--- 所有测试执行完毕 ---")
        else:
            print("\n❌ 测试中止: 未能加载真实的分析数据，请确保 output_info/ 目录中有有效的 .json 文件。")