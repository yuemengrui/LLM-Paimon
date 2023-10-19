# *_*coding:utf-8 *_*
# @Author : YueMengRui
import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, TEXT, JSON
from .db_mysql import Base


class BaseModel(object):
    """模型基类，为每个模型补充创建时间与更新时间"""
    create_time = Column(DateTime, default=datetime.datetime.now, comment="记录的创建时间")
    update_time = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now,
                         comment="记录的更新时间")


class FileSystem(Base, BaseModel):
    __tablename__ = 'file_system'
    id = Column(Integer, primary_key=True)
    file_hash = Column(String(64), nullable=False, index=True)
    file_type = Column(String(256))
    file_ext = Column(String(32))
    file_size = Column(Integer, default=0)
    base_dir = Column(String(256))


class UserFileSystem(Base, BaseModel):
    __tablename__ = 'user_file_system'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    file_hash = Column(String(64), nullable=False, index=True)
    file_name = Column(String(256))
    file_type = Column(String(256))
    file_size = Column(Integer, default=0)
    base_dir = Column(String(256))


class User(Base, BaseModel):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), nullable=False, unique=True, index=True)
    password = Column(String(256), nullable=False)


class App(Base, BaseModel):
    __tablename__ = 'app'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    kb_id = Column(Integer)
    name = Column(String(32), nullable=False)
    llm_name = Column(String(32), nullable=False)
    is_delete = Column(Boolean, default=False)
    is_multiQueryRetriever_enabled = Column(Boolean, default=True, comment="是否启用 multiquery retriever")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "llm_name": self.llm_name,
            "kb_id": self.kb_id,
            "kb_name": ''
        }


class ChatRecord(Base, BaseModel):
    __tablename__ = 'chat_record'
    id = Column(Integer, primary_key=True)
    app_id = Column(Integer, nullable=False)
    name = Column(String(16))
    dynamic_name = Column(String(16))
    is_delete = Column(Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "app_id": self.app_id,
            "name": self.name if self.name else self.dynamic_name
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
    is_delete = Column(Boolean, default=False)
    is_multiQueryRetriever_enabled = Column(Boolean, default=False, comment="是否启用 multiquery retriever")

    def to_dict(self):
        return {
            "id": self.uid,
            "uid": self.uid,
            "chat_id": self.chat_id,
            "role": self.role,
            "content": self.content,
            "response": self.response,
            "llm_name": self.llm_name
        }


class MultiQueryRetriever(Base, BaseModel):
    __tablename__ = 'multiquery_retriever'
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, nullable=False)
    origin_query = Column(TEXT, nullable=False)
    generate_query = Column(TEXT, nullable=False)


class KnowledgeBase(Base, BaseModel):
    __tablename__ = 'knowledge_base'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String(32), nullable=False)
    emb_model_list = Column(String(512), nullable=False)
    is_delete = Column(Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "embedding_model_list": eval(self.emb_model_list)
        }


class KBData(Base, BaseModel):
    __tablename__ = 'kb_data'
    id = Column(Integer, primary_key=True)
    kb_id = Column(Integer, nullable=False)
    method_id = Column(Integer, nullable=False, comment='1:自动分段，2:QA拆分， 3:json导入')
    file_name = Column(String(128), nullable=False)
    file_hash = Column(String(64), nullable=False)
    file_type = Column(String(256))
    file_size = Column(Integer, default=0)
    file_url = Column(String(256))
    data_total = Column(Integer, default=0)
    is_disable = Column(Boolean, default=False)
    is_delete = Column(Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "method_id": self.method_id,
            "file_name": self.file_name,
            "file_hash": self.file_hash,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "file_url": self.file_url,
            "data_total": self.data_total,
            "create_time": self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            "is_disable": self.is_disable
        }


class KBDataDetail(Base, BaseModel):
    __tablename__ = 'kb_data_detail'
    id = Column(Integer, primary_key=True)
    data_id = Column(Integer, nullable=False)
    content = Column(TEXT, nullable=False)
    content_hash = Column(String(64), nullable=False)

    def to_dict(self):
        return {
            "id": self.id
        }
