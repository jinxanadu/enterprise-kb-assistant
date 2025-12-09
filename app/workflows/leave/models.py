from enum import Enum
from typing import Optional, List, TypedDict, Any
from pydantic import BaseModel, Field

class LeaveType(str, Enum):
    annual = "annual"      # 年假
    sick = "sick"          # 病假
    personal = "personal"  # 事假
    other = "other"

class LeaveRequest(BaseModel):
    requester: str
    leave_type: LeaveType = LeaveType.annual
    start_time: Optional[str] = None  # "2025-11-26 09:00"
    end_time: Optional[str] = None
    duration_days: Optional[float] = None
    reason: Optional[str] = None

class LeaveState(TypedDict, total=False):
    text: str
    requester: str
    user_role: str

    req: dict            # LeaveRequest as dict
    missing_fields: List[str]
    violations: List[str]

    answer: str
    confirmed: bool
    leave_id: Optional[str]