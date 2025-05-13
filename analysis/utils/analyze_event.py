import requests
from typing import Dict, Tuple, Optional
import json
import os

# 配置参数
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("环境变量 API_KEY 未设置")  # 替换为你的实际API Key
MODEL = "glm-4-flash"  # 选择模型，如 glm-4, glm-4-long 等
URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# 构造请求头
headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

# 分析内容的系统提示词
analyze_system_prompt = """
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

# 生成解决方案的系统提示词
solution_system_prompt = """
你是一位专业的社区物业管理专家，需要针对居民的投诉/建议提供专业、切实可行的解决方案。
请根据以下内容，生成一个包含以下字段的JSON对象：

1. 'analysis': 对问题的简要分析（100-150字）
2. 'solutions': 包含2-3条具体的解决方案建议的数组，每条建议50-80字
3. 'followup': 后续跟进措施（50-80字）

输出格式必须为有效的JSON格式，不含任何额外标记或注释。

【示例】
输入：
类别：环境卫生与秩序类
问题内容：小区垃圾分类点太远，建议每栋楼下设投放点

输出：
{
  "analysis": "居民反映小区垃圾分类投放点距离较远，增加了居民垃圾分类的不便，降低了居民参与垃圾分类的积极性。合理设置垃圾分类投放点是提高小区垃圾分类效率和居民满意度的关键。",
  "solutions": [
    "在保证不影响小区环境和居民通行的前提下，在每栋楼下增设小型垃圾分类投放点，配备分类标识清晰的垃圾桶",
    "设计合理的收运路线和时间表，确保新增投放点的垃圾及时清运，避免异味和环境问题",
    "组织垃圾分类宣传活动，提高居民垃圾分类意识和参与度"
  ],
  "followup": "定期收集居民对新增投放点的使用反馈，根据反馈及时调整布局和管理方式，持续优化小区垃圾分类系统"
}
"""

def call_model_api(prompt: str, sys_prompt: str) -> Dict:
    """调用大模型API并返回结果"""
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.5,  # 可选参数，控制输出随机性
        "max_tokens": 1024,  # 可选参数，控制输出长度
    }
    
    response = requests.post(URL, headers=headers, json=payload)
    if response.status_code == 200:
        result = response.json()
        data = result["choices"][0]["message"]["content"]
        cleaned_content = data.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_content)
    else:
        raise Exception(f"请求失败: {response.status_code} - {response.text}")

def analyze_content(content: str) -> Tuple[str, str, str]:
    """分析内容获取类型、标题和类别"""
    try:
        json_data = call_model_api(content, analyze_system_prompt)
        print(f"内容分析结果: {json_data}")
        content_type = "suggest" if json_data["type"] == "建议" else "complaint" 
        return content_type, json_data["title"], json_data["category"]
    except Exception as e:
        print(f"AI分析失败: {str(e)}")
        return "complaint", "一个投诉", "物业纠纷类"

def generate_solution(category: str, content: str) -> Optional[Dict]:
    """生成详细的解决方案建议"""
    try:
        prompt = f"""
类别：{category}
问题内容：{content}
"""
        solution_data = call_model_api(prompt, solution_system_prompt)
        print(f"解决方案生成结果: {solution_data}")
        return solution_data
    except Exception as e:
        print(f"生成解决方案失败: {str(e)}")
        return None
