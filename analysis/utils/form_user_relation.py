"""
处理表单用户关系的实用函数
"""
import logging
from .analyze_event import generate_solution
from django.db import transaction

# 配置日志
logger = logging.getLogger(__name__)

def find_user_by_openid(Users, openid):
    """
    通过openid查找用户
    
    Args:
        Users: Users模型类
        openid: 用户的openid
        
    Returns:
        用户对象，如果未找到则返回None
    """
    try:
        from user.models import Users
        return Users.objects.filter(openid=openid).first()
    except Exception as e:
        logger.error(f"查找用户失败: {str(e)}")
        return None

def check_mainform_fields_ready(main_form):
    """
    检查MainForm实例的必要字段是否已经准备好
    
    Args:
        main_form: MainForm实例
        
    Returns:
        bool: 如果必要字段已准备好则返回True，否则返回False
    """
    if not main_form:
        return False
        
    # 检查必要的字段
    required_fields = ['category', 'title', 'serial_number']
    for field in required_fields:
        if not getattr(main_form, field, None):
            return False
            
    return True

def generate_solution_suggestion(category, content):
    """
    使用大模型API生成解决方案建议
    
    Args:
        category: 表单分类
        content: 投诉内容
        
    Returns:
        生成的解决方案字典，包含分析、解决方案和后续跟进措施，如果失败则返回None
    """
    try:
        if not content:
            logger.warning("表单没有内容，无法生成建议")
            return None
        
        # 添加延迟，避免与MainForm中的大模型调用冲突
        # 此处使用小延迟确保不会同时调用大模型API
        import time
        time.sleep(3)  # 延迟3秒
        
        # 使用generate_solution生成具体的解决方案
        try:
            solution_data = generate_solution(category, content)
            if solution_data and isinstance(solution_data, dict):
                return format_solution_text(solution_data)
            else:
                logger.warning("解决方案生成结果无效")
                return {
                    "title": "默认解决方案", 
                    "analysis": "很抱歉，无法生成完整解决方案。", 
                    "solutions": ["请物业工作人员进一步了解具体情况。"], 
                    "followup": "我们将尽快安排专人处理您的问题。"
                }
        except Exception as e:
            logger.error(f"生成解决方案建议失败: {str(e)}")
            return {
                "title": "默认解决方案",
                "analysis": "系统生成解决方案时遇到问题。",
                "solutions": ["请物业工作人员处理此问题。"],
                "followup": "我们将安排专人跟进处理。"
            }
    except Exception as e:
        logger.error(f"生成建议过程中发生错误: {str(e)}")
        return None

def format_solution_text(solution_data):
    """
    将解决方案数据格式化为可读文本
    
    Args:
        solution_data: 解决方案数据字典
    
    Returns:
        格式化后的文本字符串
    """
    if not solution_data or not isinstance(solution_data, dict):
        return "无法生成解决方案建议"
    
    try:
        text = f"【问题分析】\n{solution_data.get('analysis', '无分析结果')}\n\n"
        
        # 添加解决方案摘要（如果存在）
        if 'solution_summary' in solution_data and solution_data['solution_summary']:
            text += "【解决方案摘要】\n"
            if isinstance(solution_data['solution_summary'], list):
                text += solution_data['solution_summary'][0] + "\n\n"
            else:
                text += str(solution_data['solution_summary']) + "\n\n"
            
        text += "【解决方案】\n"
        for i, solution in enumerate(solution_data.get('solutions', []), 1):
            text += f"{i}. {solution}\n"
        text += f"\n【后续跟进】\n{solution_data.get('followup', '将安排专人处理您的问题')}"
        return text
    except Exception as e:
        logger.error(f"格式化解决方案文本失败: {str(e)}")
        return "解决方案格式化出错"
