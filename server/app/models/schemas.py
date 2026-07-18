from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str
    user_group: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    role: str
    user_group: str
    is_active: bool
    created_at: datetime
    password: Optional[str] = None

    class Config:
        from_attributes = True


class UserCreateRequest(UserBase):
    password: str
    role: Optional[str] = "operator"
    user_group: Optional[str] = "未分组"


class UserUpdateRequest(BaseModel):
    role: Optional[str] = None
    user_group: Optional[str] = None
    is_active: Optional[bool] = None


class HeartbeatRequest(BaseModel):
    client_id: str
    hostname: str
    ip: str
    version: str


class ActionItem(BaseModel):
    seq: int
    action_type: str
    content: Optional[str] = None
    result: Optional[str] = None
    exit_code: int = 0
    timestamp: float


class SyncRequest(BaseModel):
    client_id: str
    actions: List[ActionItem]


class ClientResponse(BaseModel):
    id: int
    client_id: str
    hostname: str
    ip_address: str
    organization: Optional[str]
    status: str
    last_heartbeat: Optional[float]
    version: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ActionResponse(BaseModel):
    id: int
    client_id: int
    action_type: str
    content: Optional[str]
    result: Optional[str]
    exit_code: int
    timestamp: float
    created_at: datetime
    client_hostname: Optional[str] = None

    class Config:
        from_attributes = True


class AIExtractedResponse(BaseModel):
    id: int
    client_id: int
    type: str
    value: Any
    confidence: float
    extracted_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_clients: int
    online_clients: int
    offline_clients: int
    total_actions: int
    actions_today: int
    pen_test_count: int
    tool_count: int
    ports_found: int
    services_found: int
    vulnerabilities_found: int
    credentials_found: int


class VideoResponse(BaseModel):
    id: int
    client_id: int
    session_id: str
    nonce: str
    file_size: int
    duration: float
    timestamp: float
    created_at: datetime
    ip_address: str = ""
    hostname: str = ""

    class Config:
        from_attributes = True


class PenTestResultResponse(BaseModel):
    id: int
    target_ip: str
    target_organization: Optional[str]
    attacker_ip: Optional[str]
    file_name: str
    file_size: int
    file_type: Optional[str]
    remark: Optional[str]
    category: str
    user_group: Optional[str] = None
    created_by: Optional[int] = None
    created_by_username: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ToolVersionResponse(BaseModel):
    id: int
    version: str
    file_name: Optional[str]
    file_size: int
    platform: str
    url: Optional[str]
    file_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ToolResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category: str
    url: Optional[str]
    created_at: datetime
    versions: List[ToolVersionResponse]

    class Config:
        from_attributes = True


class TaskTargetResponse(BaseModel):
    id: int
    plan_id: int
    target_value: str
    target_organization: Optional[str]
    progress: int
    organization: Optional[str]
    assigned_team: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class TaskPlanResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    team: str
    status: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    targets: List[TaskTargetResponse]

    class Config:
        from_attributes = True


class AssetResponse(BaseModel):
    id: int
    ip_address: str
    organization: str
    purpose: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AssetCreateRequest(BaseModel):
    ip_address: str
    organization: str
    purpose: Optional[str] = None


class AssetUpdateRequest(BaseModel):
    ip_address: Optional[str] = None
    organization: Optional[str] = None
    purpose: Optional[str] = None


class ChatRoomResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_by: int
    created_by_username: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    unread_count: Optional[int] = 0
    member_count: Optional[int] = 0
    members: Optional[List[dict]] = []

    class Config:
        from_attributes = True


class ChatRoomCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    member_ids: Optional[List[int]] = []


class ChatMessageResponse(BaseModel):
    id: int
    room_id: int
    user_id: int
    username: str
    content: Optional[str]
    message_type: str
    file_path: Optional[str]
    file_name: Optional[str]
    file_size: Optional[int]
    reply_to: Optional[int]
    reply_content: Optional[str]
    reply_username: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessageCreateRequest(BaseModel):
    room_id: int
    content: Optional[str] = None
    message_type: Optional[str] = "text"
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = 0
    reply_to: Optional[int] = None
