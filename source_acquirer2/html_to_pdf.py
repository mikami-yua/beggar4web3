# source_acquirer2/html_to_pdf.py

import requests
from bs4 import BeautifulSoup
import pdfkit
import os


def convert_url_to_pdf(article_url: str, output_path: str) -> bool:
    """
    访问给定的URL，提取其内容，并保存为PDF。
    """
    print(f"[*] 正在处理URL: {article_url}")
    try:
        # 使用浏览器User-Agent，避免被一些网站拦截
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(article_url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 这是一个需要不断优化的部分，我们加入了之前为Benzinga找到的规则
        content_body = soup.find('div', class_='article-body-content') or \
                       soup.find('article') or \
                       soup.find('div', class_='article-body') or \
                       soup.find('div', class_='caas-body')  # 适配Yahoo Finance

        if not content_body:
            print(f"⚠️ 在 {article_url} 中未能找到合适的文章主体内容。")
            return False

        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else "Untitled"

        # 将标题和正文组合成一个简单的HTML进行转换
        html_content = f"<html><head><meta charset='utf-8'><title>{title}</title></head><body><h1>{title}</h1>{content_body.prettify()}</body></html>"

        # pdfkit的选项，可以优化输出效果
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