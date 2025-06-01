import requests
from typing import Tuple
import json
from utils.env_loader import env_vars

# 配置参数
API_KEY = env_vars.API_KEY  # 从环境变量中获取API密钥

MODEL = "glm-4-flash"  # 选择模型，如 glm-4, glm-4-long 等
URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# 构造请求头
headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
system_prompt = """
你是一个严格的JSON格式生成器，请根据用户输入生成包含以下字段的JSON对象：
1. 'title'：15字以内的文案总结（动宾结构，如"建议延长营业时间"）
2. 'type'：必须为"建议"或"诉求"
3. 'category'：必须为"物业纠纷类"、"公共设施维护类"、"环境卫生与秩序类"、"邻里矛盾类"

【处理规则】
1. 类型判定标准：
   - 含改进方案/期望措施 → "建议"
   - 含权益主张/问题投诉 → "诉求"
2. 分类判定标准：
   - 物业纠纷类：涉及物业服务、费用、管理责任等问题
   - 公共设施维护类：涉及设施损坏、安全隐患、维修问题
   - 环境卫生与秩序类：涉及垃圾、噪音、违建、宠物管理等
   - 邻里矛盾类：居民之间的直接纠纷
3. 输出要求：
   - 必须直接输出标准JSON格式
   - 禁止包含```json标记或任何注释
   - 禁止换行符和多余空格

【示例】
输入：小区垃圾分类点太远，建议每栋楼下设投放点
输出：{"title":"建议增设楼下垃圾投放点","type":"建议","category":"环境卫生与秩序类"}

输入：物业擅自提高地下车库收费标准
输出：{"title":"投诉物业违规调涨停车费","type":"诉求","category":"物业纠纷类"}

输入：楼上住户深夜持续制造噪音
输出：{"title":"投诉深夜噪音扰民","type":"诉求","category":"邻里矛盾类"}
"""


def analyze_content(content: str) -> Tuple[str, str]:
    """同步分析内容获取类型和标题"""
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ],
        "temperature": 0.5,  # 可选参数，控制输出随机性
        "max_tokens": 1024,  # 可选参数，控制输出长度
    }
    try:
        response = requests.post(URL, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            data = result["choices"][0]["message"]["content"]
            cleaned_content = data.strip().replace("```json", "").replace("```", "").strip()
            json_data = json.loads(cleaned_content)
            print(json_data)
            type = "suggest" if json_data["type"] == "建议" else "complaint" 
            return type, json_data["title"], json_data["category"]
        else:
            print(f"请求失败: {result.status_code} - {result.text}")
            return "complaint", "一个投诉"
    except Exception as e:
        print(f"AI分析失败: {str(e)}")
        return "complaint", "一个投诉"
