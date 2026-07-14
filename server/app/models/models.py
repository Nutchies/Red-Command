from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="operator")
    user_group = Column(String(50), default="未分组")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String(32), unique=True, index=True, nullable=False)
    hostname = Column(String(255))
    ip_address = Column(String(45))
    organization = Column(String(255))
    status = Column(String(20), default="offline")
    last_heartbeat = Column(Float)
    version = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    actions = relationship("Action", back_populates="client")


class Action(Base):
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String(50), nullable=False)
    content = Column(Text)
    result = Column(Text)
    exit_code = Column(Integer, default=0)
    timestamp = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    client = relationship("Client", back_populates="actions")


class AIExtracted(Base):
    __tablename__ = "ai_extracted"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    source_action_id = Column(Integer, ForeignKey("actions.id"))
    type = Column(String(50), nullable=False)
    value = Column(JSON, nullable=False)
    confidence = Column(Float, default=1.0)
    extracted_at = Column(DateTime(timezone=True), server_default=func.now())


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String(64), index=True, nullable=False)
    file_path = Column(String(500), nullable=False)
    nonce = Column(String(100), nullable=False)
    file_size = Column(Integer, default=0)
    duration = Column(Float, default=0)
    timestamp = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PenTestResult(Base):
    __tablename__ = "pen_test_results"

    id = Column(Integer, primary_key=True, index=True)
    target_ip = Column(String(45), nullable=False, index=True)
    target_organization = Column(String(255))
    attacker_ip = Column(String(45))
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    file_type = Column(String(50))
    remark = Column(Text)
    category = Column(String(50), default="other")
    user_group = Column(String(50), default="未分组")
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    creator = relationship("User")


class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    category = Column(String(50), default="other")
    url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    versions = relationship("ToolVersion", back_populates="tool", cascade="all, delete-orphan")


class ToolVersion(Base):
    __tablename__ = "tool_versions"

    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(Integer, ForeignKey("tools.id", ondelete="CASCADE"), nullable=False)
    version = Column(String(50), nullable=False)
    file_path = Column(String(500))
    file_name = Column(String(255))
    file_size = Column(Integer, default=0)
    platform = Column(String(50), default="linux")
    url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tool = relationship("Tool", back_populates="versions")


class TaskPlan(Base):
    __tablename__ = "task_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    team = Column(String(100), nullable=False)
    status = Column(String(20), default="pending")
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    targets = relationship("TaskTarget", back_populates="plan", cascade="all, delete-orphan")
    creator = relationship("User")


class TaskTarget(Base):
    __tablename__ = "task_targets"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("task_plans.id", ondelete="CASCADE"), nullable=False)
    target_value = Column(String(500), nullable=False)
    target_organization = Column(String(255))
    priority = Column(String(10), default="medium")
    progress = Column(Integer, default=0)
    notes = Column(Text)
    assigned_to = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    plan = relationship("TaskPlan", back_populates="targets")


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), nullable=False, index=True)
    organization = Column(String(255), nullable=False, index=True)
    purpose = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    created_by_user = relationship("User")
    messages = relationship("ChatMessage", back_populates="room", cascade="all, delete-orphan")
    members = relationship("ChatRoomMember", back_populates="room", cascade="all, delete-orphan")


class ChatRoomMember(Base):
    __tablename__ = "chat_room_members"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    room = relationship("ChatRoom", back_populates="members")
    user = relationship("User")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text)
    message_type = Column(String(20), default="text")
    file_path = Column(String(500))
    file_name = Column(String(255))
    file_size = Column(Integer, default=0)
    reply_to = Column(Integer, ForeignKey("chat_messages.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    room = relationship("ChatRoom", back_populates="messages")
    user = relationship("User")
    reply_message = relationship("ChatMessage", remote_side=[id])
