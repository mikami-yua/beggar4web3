# source_acquirer/alphavantage_client.py

import requests
import config


def fetch_and_filter_news(tickers: list, authoritative_sources: list, api_key: str, mock_data: dict = None) -> list:
    """
    调用Alpha Vantage API获取新闻，并根据权威来源列表进行筛选。

    :param tickers: 一个包含公司股票代码的列表，如 ['AAPL', 'IBM']。
    :param authoritative_sources: 一个包含权威媒体名称的列表。
    :param api_key: 您的Alpha Vantage API Key。
    :param mock_data: (可选) 用于测试的本地JSON数据，如果提供，则不发起真实API请求。
    :return: 一个包含被筛选后的新闻信息的字典列表。
    """
    if mock_data:
        print("[*] [Mock Mode] 正在使用本地模拟数据进行处理...")
        api_response_json = mock_data
    else:
        # --- 发起真实的API请求 ---
        tickers_str = ",".join(tickers)
        # 我们一次性获取200条，最大化利用单次API调用
        url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={tickers_str}&limit=200&apikey={api_key}'

        print(f"[*] 正在向Alpha Vantage API发起请求: {url.replace(api_key, 'YOUR_API_KEY')}")

        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()  # 如果请求失败 (如 4xx or 5xx 错误), 则抛出异常
            api_response_json = response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API请求失败: {e}")
            return []

    # --- 处理和筛选返回的数据 ---
    if "feed" not in api_response_json:
        print(f"⚠️ API返回的数据格式不正确或包含错误信息: {api_response_json}")
        return []

    filtered_news = []
    all_news = api_response_json.get("feed", [])

    print(f"[*] API返回了 {len(all_news)} 条新闻，开始根据权威来源进行筛选...")

    for article in all_news:
        source = article.get("source", "Unknown")
        if source in authoritative_sources:
            # 如果来源在我们的白名单里，就提取需要的信息
            filtered_news.append({
                "title": article.get("title"),
                "url": article.get("url"),
                "summary": article.get("summary"),
                "source": source,
                "time_published": article.get("time_published"),
                "authors": article.get("authors", [])
            })

    print(f"[*] 筛选完成，保留了 {len(filtered_news)} 条权威新闻。")
    return filtered_news