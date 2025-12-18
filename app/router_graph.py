from __future__ import annotations
import re
from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END
from app.rag.qa_graph import build_qa_graph
from app.workflows.leave.leave_graph import build_leave_graph

class RouterState(TypedDict, total=False):  # 顶层状态结构，total=False表示下面所有字段都是可选的
    question: str  # 给QA的问题
    text: str  # 用户原始文本
    user_role: str  # 用户角色
    mode: str  # 模式标记，"qa"/"rag"/"kb"/"leave" 可选提示
    answer: str  # 答案
    docs: list[Any]  # QA检索到的文档列表
    requester: str
    active_route: str

    # --- fields produced by subgraphs that we want to keep across turns ---
    req: dict
    missing_fields: list[str]
    violations: list[str]

    answer: str
    leave_id: str

def decide_route(state: RouterState) -> str:
    mode = (state.get("mode") or "").lower().strip()
    active = (state.get("active_route") or "").lower().strip()

    # 如果当前已在 leave 流程中，且没有显式切换回 QA，则继续走 leave
    if active == "leave" and mode not in {"qa", "rag", "kb"}:
        return "leave"

    # 显式 mode 优先
    if mode in {"qa", "rag", "kb"}:
        return "qa"
    if mode in {"leave", "hr"}:
        return "leave"

    # 提取文本
    text = (state.get("text") or state.get("question") or "").lower()

    # === 新增：检查是否包含请假单 ID（LV- 开头）===
    if re.search(r"\blv-[0-9a-f]{6,12}\b", text):
        return "leave"

    # === 扩展关键词：覆盖申请 + 审批场景 ===
    leave_keywords = {
        # 用户申请类
        "请假", "年假", "病假", "事假", "调休", "休假", "假期",
        "请一天假", "请半天假", "休几天", "我想请",
        # HR 审批/操作类
        "审批", "批准", "通过", "同意", "驳回", "拒绝", "不通过",
        "撤销", "取消", "作废", "查", "查询", "状态", "进度",
        "请假单", "请假记录", "我的假", "历史请假"
    }

    if any(kw in text for kw in leave_keywords):
        return "leave"

    return "qa"


def route_node(state: RouterState) -> dict:
    """Router node runnable. Must return dict updates."""
    return {"active_route": decide_route(state)}


def build_router_graph():
    qa_graph = build_qa_graph()
    leave_graph = build_leave_graph()

    g = StateGraph(RouterState)

    g.add_node("route", route_node)
    g.add_node("qa", qa_graph)
    g.add_node("leave", leave_graph)

    g.add_edge(START, "route")

    g.add_conditional_edges(
        "route",
        decide_route,
        {"qa": "qa", "leave": "leave"},
    )

    g.add_edge("qa", END)
    g.add_edge("leave", END)

    return g.compile()


router_graph = build_router_graph()

