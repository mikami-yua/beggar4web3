# source_acquirer/html_to_pdf.py (v2 - 增加了对Benzinga的适配)

import requests
from bs4 import BeautifulSoup
import pdfkit
import os


def convert_url_to_pdf(article_url: str, output_path: str) -> bool:
    print(f"[*] 正在处理URL: {article_url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(article_url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # --- vvv 这里是核心改动 vvv ---
        # 我们将为不同网站找到的规则，都用 or 连接起来，程序会依次尝试
        content_body = soup.find('div', class_='article-body-content') or \
                       soup.find('article') or \
                       soup.find('div', class_='article-body') or \
                       soup.find('div', class_='caas-body') or \
                       soup.find('div', class_='content-container')
        # --- ^^^ 这里是核心改动 ^^^ ---

        if not content_body:
            print(f"⚠️ 在 {article_url} 中未能找到合适的文章主体内容。")
            return False

        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else "Untitled"

        html_content = f"<html><head><meta charset='utf-8'><title>{title}</title></head><body><h1>{title}</h1>{content_body.prettify()}</body></html>"

        options = {
            'encoding': "UTF-8",
            'custom-header': [('Accept-Encoding', 'gzip')],
            '--no-stop-slow-scripts': None,
            '--enable-local-file-access': None
        }

        pdfkit.from_string(html_content, output_path, options=options)
        print(f"✅ 成功将URL内容转换为PDF: {output_path}")
        return True

    except Exception as e:
        print(f"❌ 处理URL {article_url} 时发生错误: {e}")
        return False