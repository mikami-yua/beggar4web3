# test_content_extractor.py (v2 - 升级版，会保存全文到文件)

import os
import config
from ut.content_extractor import extract_article_text_from_url

# --- 我们测试的URL列表保持不变 ---
URLS_TO_TEST = [
    {
        "source": "Business Insider",
        "url": "https://www.businessinsider.com/ai-amazon-prime-video-content-spending-netflix-youtube-morgan-stanley-2025-7"
    },
    {
        "source": "Fortune",
        "url": "https://fortune.com/2025/07/11/linda-yaccarino-x-elon-musk-nondisclosure/"
    }
]

# --- 新增：创建一个专门存放提取出的全文文本的目录 ---
FULL_TEXT_OUTPUT_DIR = "test_full_text_output"
os.makedirs(FULL_TEXT_OUTPUT_DIR, exist_ok=True)


def run_extraction_test_and_save():
    """
    对一个URL列表进行批量内容提取，并将完整结果保存到文本文件中。
    """
    print("=" * 60)
    print("=  启动 ScrapingBee 内容提取模块单元测试  =")
    print("=  (本次测试将把全文保存到文件中)  =")
    print("=" * 60)

    if not hasattr(config, 'SCRAPINGBEE_CONFIG') or "YOUR_SCRAPINGBEE_API_KEY" in config.SCRAPINGBEE_CONFIG.get(
            "api_key", ""):
        print("❌ 测试中止: 请先在 config.py 中配置您的 ScrapingBee API Key。")
        return

    for i, article in enumerate(URLS_TO_TEST, 1):
        print(f"\n--- [ {i}/{len(URLS_TO_TEST)} ] 正在测试来自 {article['source']} 的链接 ---")

        full_text = extract_article_text_from_url(article['url'])

        print("\n--- 测试结果 ---")
        if full_text:
            # --- 核心改动：将全文保存到文件 ---
            output_filename = f"{i}_{article['source']}_full_text.txt"
            output_path = os.path.join(FULL_TEXT_OUTPUT_DIR, output_filename)

            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"Source URL: {article['url']}\n\n")
                    f.write("=" * 40 + "\n\n")
                    f.write(full_text)

                print(f"✅ 成功！已将获取到的完整全文保存至:")
                print(f"   -> {output_path}")

            except Exception as e:
                print(f"❌ 失败！在保存文件时发生错误: {e}")

        else:
            print("❌ 失败！未能获取到文章全文。请检查上面的错误日志。")
        print("=" * 60)


if __name__ == "__main__":
    run_extraction_test_and_save()
    print("\n测试脚本执行完毕。")
    print(f"请检查项目下的 '{FULL_TEXT_OUTPUT_DIR}' 文件夹以查看完整内容。")