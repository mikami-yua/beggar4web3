# analysis_note/prompt_manager.py
import json


def get_news_analysis_prompt(custom_instructions: dict) -> str:
    """
    生成包含定制化分析焦点的新闻分析MCP指令。
    :param custom_instructions: 从JSON配置文件加载的字典。
    """
    # --- 基础JSON输出格式 ---
    base_json_format = {
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
            "image_description": "...",
            "relevance_to_text": "..."
        }],
        "potential_bias": {
            # --- vvv 这里是修正的地方 vvv ---
            # 我们将它修改为一个字符串来说明期望的类型，而不是一个数学运算
            "is_biased": "true or false (boolean)",
            # --- ^^^ 这里是修正的地方 ^^^ ---
            "bias_description": "..."
        }
    }

    # --- 动态构建定制化部分 ---
    custom_analysis_section = ""
    analysis_targets = custom_instructions.get("analysis_targets", {})
    output_structure = custom_instructions.get("custom_output_structure", {})

    if analysis_targets and output_structure:
        # 1. 动态为Prompt添加定制化指令
        target_companies_str = ", ".join(analysis_targets.get("target_companies", []))
        target_keywords_str = ", ".join(analysis_targets.get("target_price_keywords", []))

        custom_analysis_section = f"""
    7.  **定制化信息提取**: 请特别注意，如果文档中提及以下任何一家公司 ({target_companies_str})，请使用以下关键词 ({target_keywords_str}) 寻找并提取其目标价格和分析师评级等关键信息。
"""
        # 2. 动态为输出JSON格式添加新字段
        custom_field_name = output_structure.get("field_name", "custom_analysis")
        base_json_format[custom_field_name] = [output_structure.get("format", {})]

    # --- 组合最终的Prompt ---
    final_json_instruction = json.dumps(base_json_format, indent=4, ensure_ascii=False)

    prompt = f"""
    ### 指令 ###
    你是一位专业的金融及新闻分析师。请对用户上传的PDF文档进行深入分析。文档中可能包含文字和图片，请综合所有信息进行回答。

    ### 分析框架 (MCP) ###
    1.  **摘要总结**: 总结文档的核心内容 (不超过300字)。
    2.  **主题识别**: 识别出文档讨论的3-5个关键主题。
    3.  **实体提取**: 找出文中提到的重要人物、组织和地点。
    4.  **情感判断**: 评估文档的整体情感基调。
    5.  **图片分析**: 如果文档中有图片，请描述每张图片的内容，并分析它与文本内容的关系。
    6.  **偏见审视**: 分析文档是否存在明显的立场偏见。
{custom_analysis_section}
    ### 输出格式 ###
    请务必以一个严格的JSON对象格式返回你的分析结果，不要包含任何JSON格式之外的额外解释或说明。JSON结构如下：
    ```json
    {final_json_instruction}
    ```

    ### 分析结果 (JSON) ###
    """
    return prompt