# batch_test_url_to_pdf.py

import os
from ut.html_to_pdf import convert_url_to_pdf

# --- 我们将您提供的两个链接放入一个列表中 ---
TEST_URLS = [
    {
        "source": "Business Insider",
        "url": "https://www.businessinsider.com/ai-amazon-prime-video-content-spending-netflix-youtube-morgan-stanley-2025-7"
    },
    {
        "source": "Fortune",
        "url": "https://fortune.com/2025/07/11/linda-yaccarino-x-elon-musk-nondisclosure/"
    }
]

# 创建一个专门的输出目录来存放测试PDF
TEST_OUTPUT_DIR = "batch_test_pdf_output"
os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)


def run_batch_conversion_test():
    """
    对一个URL列表进行批量转换测试。
    """
    print("=" * 50)
    print("=  开始批量测试 URL 到 PDF 的转换功能  =")
    print("=" * 50)

    success_count = 0
    failure_count = 0

    # 遍历列表中的每一个URL进行转换
    for i, article in enumerate(TEST_URLS, 1):
        print(f"\n--- [ {i}/{len(TEST_URLS)} ] 正在处理 {article['source']} 的新闻 ---")

        # 为每个PDF生成一个清晰的文件名
        output_filename = os.path.join(TEST_OUTPUT_DIR, f"test_{i}_{article['source']}.pdf")

        # 执行转换
        success = convert_url_to_pdf(article['url'], output_filename)

        if success:
            success_count += 1
        else:
            failure_count += 1

    print("\n" + "=" * 50)
    print("=  批量转换测试总结  =")
    print("=" * 50)
    print(f"总任务数: {len(TEST_URLS)}")
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {failure_count}")

    if failure_count == 0:
        print("\n🎉 全部转换成功！")

    print(f"\n请检查项目目录下的 '{TEST_OUTPUT_DIR}' 文件夹，")
    print("并逐一打开生成的PDF文件查看转换效果。")
    print("=" * 50)


if __name__ == "__main__":
    run_batch_conversion_test()