# source_acquirer2/content_extractor.py (v2 - 增加了对Business Insider的适配)

import requests
from bs4 import BeautifulSoup
import config


def extract_article_text_from_url(article_url: str) -> str | None:
    """
    使用ScrapingBee API从给定的URL中提取文章正文。
    """
    print(f"[*] [ScrapingBee] 正在为URL启动内容提取任务: {article_url}")

    api_key = config.SCRAPINGBEE_CONFIG.get("api_key")
    if not api_key or "YOUR_SCRAPINGBEE_API_KEY" in api_key:
        print("❌ [ScrapingBee] 错误: 未在config.py中配置API Key。")
        return None

    try:
        response = requests.get(
            url='https://app.scrapingbee.com/api/v1/',
            params={
                'api_key': api_key,
                'url': article_url,
                'render_js': 'false'
            },
            timeout=90
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # --- vvv 这里是核心改动 vvv ---
        # 我们将为不同网站找到的规则，都用 or 连接起来，程序会依次尝试
        # 将Business Insider的新规则放在最前面
        content_body = soup.find('div', class_='prose-rich-text') or \
                       soup.find('div', class_='article-body-content') or \
                       soup.find('div', class_='article-body') or \
                       soup.find('article') or \
                       soup.find('div', class_='caas-body')
        # --- ^^^ 这里是核心改动 ^^^ ---

        if content_body:
            full_text = content_body.get_text(separator='\n', strip=True)
            print("✅ [ScrapingBee] 成功提取到文章正文。")
            return full_text
        else:
            print("⚠️ [ScrapingBee] 未能在返回的HTML中找到任何匹配的文章主体容器。")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ [ScrapingBee] API请求失败: {e}")
        return None