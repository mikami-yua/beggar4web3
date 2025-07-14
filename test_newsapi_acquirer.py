# test_newsapi_acquirer.py

import config
from source_acquirer2.newsapi_client import fetch_full_content_news


def run_newsapi_test():
    """
    使用NewsAPI进行一次真实的获取和筛选测试。
    """
    print("\n--- 开始使用NewsAPI进行获取测试 ---")

    # 从配置中读取所需信息
    api_key = config.NEWSAPI_CONFIG.get("api_key")
    query = config.NEWSAPI_CONFIG.get("query_keywords")
    domains = config.NEWSAPI_CONFIG.get("domains")

    if not api_key or "YOUR_NEWSAPI_KEY_HERE" in api_key:
        print("❌ 错误: 请先在 config.py 中配置您的 NewsAPI Key。")
        return

    # 调用新的客户端函数
    articles = fetch_full_content_news(api_key, query, domains)

    print("\n" + "=" * 50)
    print("=  获取到的新闻列表  =")
    print("=" * 50)

    if not articles:
        print("未能获取到任何新闻。")
    else:
        for i, article in enumerate(articles, 1):
            print(f"\n[第 {i} 条] -----------------------------")
            print(f"  标题: {article['title']}")
            print(f"  来源: {article['source']}")
            print(f"  链接: {article['url']}")
            print(f"  全文内容 (片段): {article.get('full_content', '无内容')[:200]}...")  # 打印前200个字符预览

    print(f"\n✅ NewsAPI信息获取模块测试完成，共获取 {len(articles)} 条新闻。")


if __name__ == "__main__":
    run_newsapi_test()