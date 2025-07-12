# test_url_to_pdf.py

import os
from source_acquirer.html_to_pdf import convert_url_to_pdf


def run_single_conversion_test():
    """
    对一个真实的URL进行转换测试。
    """
    print("=" * 50)
    print("=  开始独立测试 URL 到 PDF 的转换功能  =")
    print("=" * 50)

    # 我们从上次API返回结果中，挑选一个有代表性的URL作为测试目标
    # 这是关于高盛测试AI开发者的文章，它包含标题、正文和图片
    test_url = "https://www.benzinga.com/markets/tech/25/07/46365117/goldman-bets-on-ai-developer-to-boost-productivity-could-this-be-the-future-of-wall-street-jobs"

    # 创建一个专门的输出目录来存放测试PDF，避免与主流程混淆
    test_output_dir = "test_pdf_output"
    os.makedirs(test_output_dir, exist_ok=True)
    output_filename = os.path.join(test_output_dir, "benzinga_goldman_test.pdf")

    # 执行转换
    success = convert_url_to_pdf(test_url, output_filename)

    print("\n" + "-" * 50)
    if success:
        print(f"✅ 测试成功！请检查项目目录下的 '{test_output_dir}' 文件夹，")
        print(f"   并打开文件 '{os.path.basename(output_filename)}' 查看效果。")
    else:
        print("❌ 测试失败。请检查上面的错误日志。")
    print("-" * 50)


if __name__ == "__main__":
    run_single_conversion_test()