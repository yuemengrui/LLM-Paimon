# *_*coding:utf-8 *_*
# @Author : YueMengRui
from info.configs import *
from pydantic import BaseModel, Field
from typing import Dict, List


class ErrorResponse(BaseModel):
    errcode: int
    errmsg: str


class AuthRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    token: str
    expires: int


class ChatRequest(BaseModel):
    app_id: int
    chat_id: int
    uid: str
    answer_uid: str
    model_name: str = Field(default=None, description="模型名称")
    prompt: str
    history: List = Field(default=[], description="历史记录")
    generation_configs: Dict = {}
    stream: bool = Field(default=True, description="是否流式输出")


class ChatResponse(BaseModel):
    model_name: str
    answer: str
    history: List[List[str]]
    usage: Dict


class EmbeddingRequest(BaseModel):
    model_name: str = Field(default=None, description="模型名称")
    sentences: List[str] = Field(description="句子列表")


class TokenCountRequest(BaseModel):
    model_name: str = Field(default=None, description="模型名称")
    prompt: str


class AppCreateRequest(BaseModel):
    name: str
    llm_name: str


class AppChatListRequest(BaseModel):
    app_id: int


class AppChatCreateRequest(BaseModel):
    app_id: int
    name: str = Field(default='新对话')


class AppChatMessageListRequest(BaseModel):
    chat_id: int
