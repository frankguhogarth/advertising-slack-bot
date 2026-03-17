"""
Notion集成工具
用于查询员工信息和创建项目卡片
"""

import requests
from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context

# Notion API配置
NOTION_API_KEY = "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"
NOTION_VERSION = "2022-06-28"

# Database IDs
STAFF_DATABASE_ID = "326b873e83cb80cfa8f2ca7695e5a1d5"  # 员工表
PROJECT_DATABASE_ID = "28db873e83cb80c18387e908e762609e"  # 项目表（用于查询员工当前项目数和创建新项目）


def get_headers():
    """获取Notion API请求头"""
    return {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }


def query_database(database_id: str) -> dict:
    """查询Notion数据库的所有记录"""
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    response = requests.post(url, headers=get_headers(), json={})
    
    if response.status_code != 200:
        raise Exception(f"查询数据库失败: {response.text}")
    
    return response.json()


def extract_name_from_title(page_id: str) -> str:
    """从页面ID获取标题（员工姓名）"""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    response = requests.get(url, headers=get_headers())
    
    if response.status_code != 200:
        return "未知"
    
    page_data = response.json()
    properties = page_data.get("properties", {})
    
    # 查找第一个title类型的属性
    for prop_name, prop_data in properties.items():
        if prop_data.get("type") == "title":
            titles = prop_data.get("title", [])
            return "".join([t.get("plain_text", "") for t in titles])
    
    return "未知"


# ========== 普通函数（工具内部调用） ==========

def _get_all_staff_data() -> list:
    """获取所有员工信息的普通函数（内部使用）"""
    staff_data = query_database(STAFF_DATABASE_ID)
    results = staff_data.get("results", [])
    staff_list = []
    
    for page in results:
        page_id = page.get("id", "")
        properties = page.get("properties", {})
        
        staff_info = {
            "page_id": page_id,
            "name": extract_name_from_title(page_id),
            "email": "",
            "position": "",
            "skills": ""
        }
        
        # 提取属性值
        for prop_name, prop_data in properties.items():
            prop_type = prop_data.get("type", "")
            
            if prop_type == "email":
                staff_info["email"] = prop_data.get("email", "")
            elif prop_type == "select":
                select = prop_data.get("select", {})
                if select and "position" in prop_name.lower():
                    staff_info["position"] = select.get("name", "")
                elif select and "skill" in prop_name.lower():
                    staff_info["skills"] = select.get("name", "")
            elif prop_type == "multi_select":
                selects = prop_data.get("multi_select", [])
                if "skill" in prop_name.lower():
                    staff_info["skills"] = ", ".join([s.get("name", "") for s in selects])
        
        staff_list.append(staff_info)
    
    return staff_list


def _get_staff_workload_data() -> dict:
    """获取员工工作量数据的普通函数（内部使用）"""
    project_data = query_database(PROJECT_DATABASE_ID)
    results = project_data.get("results", [])
    
    # 统计每个员工的项目数
    staff_projects = {}
    
    for page in results:
        properties = page.get("properties", {})
        
        # 查找员工关联字段（relation类型）
        for prop_name, prop_data in properties.items():
            if prop_data.get("type") == "relation" and ("user" in prop_name.lower() or "员工" in prop_name):
                relations = prop_data.get("relation", [])
                
                for relation in relations:
                    staff_page_id = relation.get("id", "")
                    staff_name = extract_name_from_title(staff_page_id)
                    
                    # 获取项目名称
                    project_name = extract_name_from_title(page.get("id", ""))
                    
                    if staff_name not in staff_projects:
                        staff_projects[staff_name] = {
                            "name": staff_name,
                            "page_id": staff_page_id,
                            "project_count": 0,
                            "projects": []
                        }
                    
                    staff_projects[staff_name]["project_count"] += 1
                    staff_projects[staff_name]["projects"].append(project_name)
    
    return staff_projects


def _find_staff_by_position_data(position: str) -> list:
    """根据职位查找员工并排序的普通函数（内部使用）"""
    # 获取所有员工信息
    staff_list = _get_all_staff_data()
    
    # 筛选匹配职位的员工
    matched_staff = []
    for staff in staff_list:
        if position.lower() in staff["position"].lower():
            matched_staff.append(staff)
    
    # 获取工作量数据
    workload_data = _get_staff_workload_data()
    
    # 创建工作量映射
    workload_map = {
        staff["name"]: staff["project_count"]
        for staff in workload_data.values()
    }
    
    # 添加工作量信息并排序
    for staff in matched_staff:
        staff["project_count"] = workload_map.get(staff["name"], 0)
    
    # 按项目数量排序（项目少的在前）
    matched_staff.sort(key=lambda x: x["project_count"])
    
    return matched_staff


# ========== 工具函数（对外暴露） ==========

@tool
def get_all_staff(runtime: ToolRuntime = None) -> str:
    """
    获取所有员工信息，包括姓名、邮箱、职位和技能
    
    Returns:
        员工信息的JSON字符串
    """
    try:
        ctx = runtime.context if runtime else new_context(method="get_all_staff")
        import json
        return json.dumps(_get_all_staff_data(), ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取员工信息失败: {str(e)}"


@tool
def get_staff_workload(runtime: ToolRuntime = None) -> str:
    """
    获取所有员工当前的工作量（正在进行的项目数量）
    
    Returns:
        员工工作量的JSON字符串，格式：[{"name": "姓名", "project_count": 数量, "projects": ["项目名1", "项目名2"]}]
    """
    try:
        ctx = runtime.context if runtime else new_context(method="get_staff_workload")
        import json
        return json.dumps(list(_get_staff_workload_data().values()), ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取员工工作量失败: {str(e)}"


@tool
def find_staff_by_position(position: str, runtime: ToolRuntime = None) -> str:
    """
    根据职位查找员工，并按工作量排序（项目少的优先）
    
    Args:
        position: 职位名称，如"设计师"、"修图师"、"完稿"
        
    Returns:
        符合条件的员工列表，按项目数量排序
    """
    try:
        ctx = runtime.context if runtime else new_context(method="find_staff_by_position")
        import json
        return json.dumps(_find_staff_by_position_data(position), ensure_ascii=False, indent=2)
    except Exception as e:
        return f"查找员工失败: {str(e)}"


@tool
def create_project_card(project_name: str, staff_names: str, start_date: str, end_date: str, client_name: str = None, runtime: ToolRuntime = None) -> str:
    """
    在Notion项目表中创建新的项目卡片
    
    Args:
        project_name: 项目名称
        staff_names: 员工姓名列表，用逗号分隔，如"Lia Liu,Wu Qiong"
        start_date: 开始日期，格式：YYYY-MM-DD
        end_date: 结束日期，格式：YYYY-MM-DD
        client_name: 客户名称（可选）
        
    Returns:
        创建结果
    """
    try:
        ctx = runtime.context if runtime else new_context(method="create_project_card")
        
        # 解析员工姓名
        staff_list = [name.strip() for name in staff_names.split(",")]
        
        # 获取员工信息以获取他们的page_id
        all_staff = _get_all_staff_data()
        
        # 创建员工姓名到page_id的映射
        staff_name_to_id = {
            staff["name"]: staff["page_id"]
            for staff in all_staff
        }
        
        # 构建员工关联数据
        staff_relations = []
        for staff_name in staff_list:
            if staff_name in staff_name_to_id:
                staff_relations.append({
                    "id": staff_name_to_id[staff_name]
                })
        
        # 构建页面数据
        page_data = {
            "parent": {
                "database_id": PROJECT_DATABASE_ID
            },
            "properties": {
                "Name": {  # 假设有一个Name字段
                    "title": [
                        {
                            "text": {
                                "content": project_name
                            }
                        }
                    ]
                },
                "Start date": {  # 假设有一个开始日期字段
                    "date": {
                        "start": start_date
                    }
                },
                "End date": {  # 假设有一个结束日期字段
                    "date": {
                        "start": end_date
                    }
                }
            }
        }
        
        # 添加客户名称（如果提供）
        if client_name:
            page_data["properties"]["Client"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": client_name
                        }
                    }
                ]
            }
        
        # 添加员工关联（如果找到员工）
        if staff_relations:
            page_data["properties"]["Staff"] = {
                "relation": staff_relations
            }
        
        # 创建页面
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers=get_headers(),
            json=page_data
        )
        
        if response.status_code != 200:
            return f"创建项目卡片失败: {response.text}"
        
        result = response.json()
        project_url = result.get("url", "")
        
        return f"✅ 项目卡片创建成功！\n项目名称: {project_name}\n员工: {', '.join(staff_list)}\n开始时间: {start_date}\n结束时间: {end_date}\n项目链接: {project_url}"
        
    except Exception as e:
        return f"创建项目卡片失败: {str(e)}"
