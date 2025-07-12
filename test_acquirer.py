# simple_alphavantage_test.py

import requests
import json

# --- 请在这里填入您的API Key ---
API_KEY = "JBMHDZQBP55ZYTTO"


# -----------------------------

def run_basic_news_test():
    """
    发起一次最基础的新闻API请求，不带任何过滤条件。
    """
    print("[*] 正在发起无过滤条件的API请求...")

    # 构造最简单的URL，只包含function和apikey
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&apikey={API_KEY}"

    try:
        response = requests.get(url, timeout=20)
        # 无论成功失败，我们都先尝试打印原始文本，看看是什么内容
        print(f"[*] API响应状态码: {response.status_code}")
        print("[*] API返回的原始文本内容:")
        print("-" * 40)

        # 尝试将返回内容作为JSON格式化打印
        try:
            data = response.json()
            print(json.dumps(data, indent=4, ensure_ascii=False))
        except json.JSONDecodeError:
            # 如果不是合法的JSON，就直接打印文本
            print(response.text)

        print("-" * 40)

        # --- 根据返回内容进行分析 ---
        if response.status_code == 200:
            data = response.json()
            # 检查是否有错误信息
            if "Error Message" in data:
                print(f"✅ 测试成功：API按预期返回了一个错误提示 -> '{data['Error Message']}'")
                print("   这说明API要求我们必须提供tickers或topics等过滤参数。")
            # 检查是否有新闻
            elif "feed" in data and data.get("feed"):
                print("✅ 测试成功：API返回了新闻数据！内容如下：")
                for i, article in enumerate(data["feed"], 1):
                    print(f"  {i}. {article.get('title')}")
            # 检查是否返回了空的新闻列表
            elif "feed" in data and not data.get("feed"):
                print("✅ 测试成功：API返回了数据，但新闻列表'feed'为空。")
            else:
                print("⚠️ 测试完成：API返回了未知结构的数据。")
        else:
            print("❌ 测试失败：收到了一个失败的HTTP状态码。")

    except requests.exceptions.RequestException as e:
        print(f"❌ 测试失败：网络请求过程中发生错误: {e}")


if __name__ == "__main__":
    if "YOUR_ALPHA_VANTAGE_API_KEY" in API_KEY:
        print("!! 请先在本脚本中填入您的Alpha Vantage API Key !!")
    else:
        run_basic_news_test()