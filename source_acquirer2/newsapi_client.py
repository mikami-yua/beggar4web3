# source_acquirer2/newsapi_client.py

from newsapi import NewsApiClient


def fetch_full_content_news(api_key: str, query: str, domains: str = None) -> list:
    """
    使用NewsAPI.org获取包含全文内容的新闻。

    :param api_key: 您的NewsAPI.org API Key。
    :param query: 搜索的关键词。
    :param domains: (可选) 筛选特定新闻网站的域名，用逗号分隔。
    :return: 包含筛选后新闻信息的字典列表。
    """
    print(f"[*] 正在从 NewsAPI.org 获取关于 '{query}' 的新闻...")

    try:
        # 初始化客户端
        newsapi = NewsApiClient(api_key=api_key)

        # 发起API请求
        # 我们使用get_everything端点，它可以搜索所有新闻
        # language='en'表示我们只想要英文新闻
        top_headlines = newsapi.get_everything(
            q=query,
            domains=domains,
            language='en',
            sort_by='publishedAt'  # 按发布时间排序
        )

        if top_headlines.get('status') != 'ok':
            print(f"❌ NewsAPI返回错误: {top_headlines.get('message')}")
            return []

        articles = top_headlines.get('articles', [])
        print(f"[*] API返回了 {len(articles)} 条新闻。")

        # 清理和格式化返回的数据
        cleaned_articles = []
        for article in articles:
            # NewsAPI的`content`字段有时会以 "[+1234 chars]" 结尾，我们把它去掉
            content = article.get('content', '')
            if content and '[+' in content:
                content = content.rsplit('[+', 1)[0].strip()

            cleaned_articles.append({
                "title": article.get("title"),
                "url": article.get("url"),
                "source": article.get("source", {}).get("name"),
                "time_published": article.get("publishedAt"),
                "full_content": content  # <--- 这是最关键的！我们直接获取了全文内容
            })

        return cleaned_articles

    except Exception as e:
        print(f"❌ 调用NewsAPI过程中发生异常: {e}")
        return []