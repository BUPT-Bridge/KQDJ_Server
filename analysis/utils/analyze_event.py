import requests
from typing import Dict, Tuple, Optional
import json
import os

# 配置参数
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("环境变量 API_KEY 未设置")  # 替换为你的实际API Key
MODEL = "glm-4-flash"  # 选择模型，如 glm-4, glm-4-long 等
URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# 构造请求头
headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}


# 生成解决方案的系统提示词
solution_system_prompt = """
"角色设定": "作为社区物业管理专家，需精准解决居民投诉并提供可行方案",
"输入要求": "接收包含【类别】和【问题内容】的结构化投诉/建议信息",
"输出规范": {
    "字段构成": [
        "analysis（100-150字问题分析）",
        "solutions（2-3条50-80字具体方案）",
        "solution_summary（25字内单条简案，数组格式）",
        "followup（50-80字跟进措施）"
    ],
    "格式约束": [
        "严格遵循JSON格式",
        "solution_summary必须为单元素数组",
        "所有字段值使用中文",
        "禁止注释/额外标记"
      ]
},
"处理逻辑": {
    "方案提炼规则": [
        "从solutions提取核心要素合并为25字内表述",
        "必须包含空间优化、流程改进、意识提升三个维度",
        "使用动宾结构短语组合"
      ],
    "验证机制": [
        "自动检测字段长度限制",
        "校验JSON格式有效性",
        "验证方案要素完整性"
      ]
},
"示例说明": {
      "输入样例": "类别：环境卫生与秩序类｜问题内容：小区垃圾分类点太远，建议每栋楼下设投放点",
      "输出样例": {
        "analysis": "居民反映垃圾分类点距离过远导致分类积极性下降，合理设置投放点位是提升管理效能的关键。",
        "solutions": [
          "在各楼栋单元门口设置分类垃圾箱，确保间距不超过50米",
          "建立早晚高峰时段动态清运机制，配置智能满溢监测装置",
          "开展入户指导并设立垃圾分类积分奖励制度"
        ],
        "solution_summary": ["楼栋增设分类箱并智能清运，推行分类积分制"],
        "followup": "每月通过业主APP收集投放点使用评价，结合清运数据动态调整设备布局"
    }
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
        "temperature": 0.7,  # 可选参数，控制输出随机性
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
