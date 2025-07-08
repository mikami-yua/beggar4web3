# analysis_note/prompt_manager.py

def get_news_analysis_prompt() -> str:
    """
    生成新闻分析的MCP指令 (不包含原文)。
    AI会从上传的文件中自行读取内容。
    """
    json_format_instruction = """
    {
      "summary": "...",
      "key_topics": ["...", "...", "..."],
      "named_entities": {
        "persons": ["...", "..."],
        "organizations": ["...", "..."],
        "locations": ["...", "..."]
      },
      "sentiment_analysis": {
        "overall_sentiment": "Positive/Negative/Neutral",
        "reasoning": "..."
      },
      "image_analysis": [{
        "image_description": "对图片内容的简要描述...",
        "relevance_to_text": "图片与文章内容的关系..."
      }],
      "potential_bias": {
        "is_biased": true/false,
        "bias_description": "..."
      }
    }
    """
    # 我在JSON中增加了一个"image_analysis"字段来体现新能力

    prompt = f"""
    ### 指令 ###
    你是一位专业的新闻分析师。请对用户上传的PDF文档进行深入分析。文档中可能包含文字和图片，请综合所有信息进行回答。

    ### 分析框架 (MCP) ###
    1.  **摘要总结**: 总结文档的核心内容 (不超过300字)。
    2.  **主题识别**: 识别出文档讨论的3-5个关键主题。
    3.  **实体提取**: 找出文中提到的重要人物、组织和地点。
    4.  **情感判断**: 评估文档的整体情感基调。
    5.  **图片分析**: 如果文档中有图片，请描述每张图片的内容，并分析它与文本内容的关系。
    6.  **偏见审视**: 分析文档是否存在明显的立场偏见。

    ### 输出格式 ###
    请务必以一个严格的JSON对象格式返回你的分析结果，不要包含任何JSON格式之外的额外解释或说明。JSON结构如下：
    ```json
    {json_format_instruction}
    ```

    ### 分析结果 (JSON) ###
    """
    return prompt