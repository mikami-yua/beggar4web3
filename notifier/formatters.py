# notifier/formatters.py

def format_analysis_for_email(analysis_data: dict, source_filename: str) -> tuple[str, str]:
    """
    将JSON格式的分析数据格式化为适合邮件发送的主题和正文。

    :param analysis_data: AI分析返回的字典。
    :param source_filename: 被分析的原始文件名。
    :return: 一个包含 (邮件主题, 邮件正文) 的元组。
    """
    # --- 生成邮件主题 ---
    subject = f"新闻分析报告: {source_filename}"

    # --- 生成邮件正文 ---
    body_parts = []
    body_parts.append(f"对文件《{source_filename}》的AI分析简报如下：")
    body_parts.append("\n" + "="*30 + "\n")

    # 1. 核心摘要
    body_parts.append("### 1. 核心摘要 ###")
    body_parts.append(analysis_data.get("summary", "无"))
    body_parts.append("\n")

    # 2. 关键主题
    body_parts.append("### 2. 关键主题 ###")
    topics = analysis_data.get("key_topics", [])
    if topics:
        for topic in topics:
            body_parts.append(f"- {topic}")
    else:
        body_parts.append("未提取到关键主题。")
    body_parts.append("\n")

    # 3. 情感与偏见分析
    body_parts.append("### 3. 情感与偏见分析 ###")
    sentiment = analysis_data.get("sentiment_analysis", {})
    bias = analysis_data.get("potential_bias", {})
    body_parts.append(f"情感倾向: {sentiment.get('overall_sentiment', '未知')}")
    body_parts.append(f"情感判断理由: {sentiment.get('reasoning', '无')}")
    body_parts.append(f"存在偏见: {'是' if bias.get('is_biased') else '否'}")
    body_parts.append(f"偏见描述: {bias.get('bias_description', '无')}")
    body_parts.append("\n")

    # 4. 定制化分析 (如果存在)
    custom_analysis = analysis_data.get("company_specific_analysis")
    if custom_analysis:
        body_parts.append("### 4. 上市公司目标价格分析 ###")
        for item in custom_analysis:
            body_parts.append(f"- 公司: {item.get('company_name', '未知')}")
            body_parts.append(f"  目标价格信息: {item.get('target_price_info', '无')}")
            body_parts.append(f"  分析师评论: {item.get('analyst_comment', '无')}")
        body_parts.append("\n")

    # 5. 命名实体
    body_parts.append("### 5. 提及的命名实体 ###")
    entities = analysis_data.get("named_entities", {})
    body_parts.append(f"- 人物: {', '.join(entities.get('persons', ['无']))}")
    body_parts.append(f"- 组织: {', '.join(entities.get('organizations', ['无']))}")
    body_parts.append(f"- 地点: {', '.join(entities.get('locations', ['无']))}")

    body = "\n".join(body_parts)

    return subject, body