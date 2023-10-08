# *_*coding:utf-8 *_*
# @Author : YueMengRui
import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, TEXT, JSON
from .db import Base


class BaseModel(object):
    """模型基类，为每个模型补充创建时间与更新时间"""
    create_time = Column(DateTime, default=datetime.datetime.now, comment="记录的创建时间")
    update_time = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now,
                         comment="记录的更新时间")


class User(Base, BaseModel):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), nullable=False, unique=True, index=True)
    password = Column(String(256), nullable=False)


class App(Base, BaseModel):
    __tablename__ = 'app'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    name = Column(String(32), nullable=False)
    llm_name = Column(String(32), nullable=False)
    is_delete = Column(Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "llm_name": self.llm_name
        }


class ChatRecord(Base, BaseModel):
    __tablename__ = 'chat_record'
    id = Column(Integer, primary_key=True)
    app_id = Column(Integer, nullable=False)
    name = Column(String(32), nullable=False)
    is_delete = Column(Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "app_id": self.app_id,
            "name": self.name
        }


class ChatMessageRecord(Base, BaseModel):
    __tablename__ = 'chat_message_record'
    id = Column(Integer, primary_key=True)
    uid = Column(String(64), nullable=False)
    chat_id = Column(Integer, nullable=False)
    role = Column(String(32), default='assistant', nullable=False)
    content = Column(TEXT, nullable=False)
    response = Column(JSON, default={})
    llm_name = Column(String(32))
    time_cost = Column(String(16))
    is_delete = Column(Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.uid,
            "role": self.role,
            "content": self.content,
            "usage": self.response['usage'] if 'usage' in self.response else {},
            "response": self.response,
            "time_cost": self.time_cost
        }
