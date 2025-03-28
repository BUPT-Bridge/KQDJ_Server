def sync_feedback_status(instance):
    """
    根据feedback_need同步更新feedback_status
    
    :param instance: MainForm实例
    """
    if instance.feedback_need:
        instance.feedback_status = 1  # 需要回访
    else:
        instance.feedback_status = 0  # 不需要回访
