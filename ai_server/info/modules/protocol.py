# *_*coding:utf-8 *_*
# @Author : YueMengRui
from pydantic import BaseModel, Field
from typing import Dict, List


class ErrorResponse(BaseModel):
    object: str = "error"
    errcode: int
    errmsg: str


class ChatRequest(BaseModel):
    model_name: str = Field(default=None, description="模型名称")
    prompt: str
    history: List = Field(default=[], description="历史记录")
    generation_configs: Dict = {}
    stream: bool = Field(default=True, description="是否流式输出")


class Usage(BaseModel):
    prompt_tokens: int
    generation_tokens: int
    total_tokens: int
    average_speed: str


class ChatResponse(BaseModel):
    object: str = 'llm.chat'
    model_name: str
    answer: str
    usage: Usage


class EmbeddingRequest(BaseModel):
    model_name: str = Field(default=None, description="模型名称")
    sentences: List[str] = Field(description="句子列表")


class TokenCountRequest(BaseModel):
    model_name: str = Field(default=None, description="模型名称")
    prompt: str
