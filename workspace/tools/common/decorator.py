# workspace/tools/common/decorator.py

def tool(func):
    """標記工具模組用的函式。"""
    func._is_tool = True
    return func

def task(task_id: str):
    def decorator(func):
        func._is_task = True
        func._task_id = task_id
        return func
    return decorator

