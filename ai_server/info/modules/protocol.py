# *_*coding:utf-8 *_*
# @Author : YueMengRui
from pydantic import BaseModel, Field
from typing import Dict, List


class ErrorResponse(BaseModel):
    errcode: int
    errmsg: str


class FileUploadResponse(BaseModel):
    file_hash: str
    file_url: str
    file_name: str
    file_size: int
    file_type: str
    file_ext: str = Field(default='')


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
    custom: Dict = Field(default={})
    """
    :param custom: {
                "tableQA": {
                    "table_content": ""
                }
            }
    """


class ChatVLImageRequest(BaseModel):
    app_id: int
    chat_id: int
    uid: str
    model_name: str = Field(default="Qwen_VL", description="模型名称")
    url: str


class ChatVLRequest(BaseModel):
    app_id: int
    chat_id: int
    uid: str
    answer_uid: str
    model_name: str
    prompt: str
    history: List = Field(default=[], description="历史记录")
    generation_configs: Dict = Field(default={})
    stream: bool = Field(default=True, description="是否流式输出")
    true_prompt: List


class ChatResponse(BaseModel):
    model_name: str
    answer: str
    history: List[List[str]]
    usage: Dict


class ChatSimpleRequest(BaseModel):
    model_name: str = Field(default=None, description="模型名称")
    prompt: str
    history: List = Field(default=[], description="历史记录")
    generation_configs: Dict = {}
    stream: bool = Field(default=True, description="是否流式输出")


class EmbeddingRequest(BaseModel):
    model_name: str = Field(default=None, description="模型名称")
    sentences: List[str] = Field(description="句子列表")


class TokenCountRequest(BaseModel):
    model_name: str = Field(default=None, description="模型名称")
    prompt: str


class AppInfoRequest(BaseModel):
    app_id: int


class AppInfoModifyRequest(BaseModel):
    app_id: int
    kb_id: int = Field(default=None)
    name: str
    llm_name: str


class AppCreateRequest(BaseModel):
    name: str
    llm_name: str
    kb_id: int = Field(default=None)


class AppCreateSystemAppRequest(BaseModel):
    system_app_id: int


class AppDeleteRequest(BaseModel):
    app_id: int


class AppChatListRequest(BaseModel):
    app_id: int


class AppChatCreateRequest(BaseModel):
    app_id: int
    name: str = Field(default=None)


class AppChatMessageListRequest(BaseModel):
    chat_id: int


class KBCreateRequest(BaseModel):
    name: str
    embedding_model_list: List[str]


class KBDeleteRequest(BaseModel):
    kb_id: int


class KBDataListRequest(BaseModel):
    kb_id: int


class KBDataImportOne(BaseModel):
    file_hash: str
    file_name: str
    file_url: str
    file_size: int
    file_type: str
    file_ext: str = Field(default='')


class KBDataImportRequest(BaseModel):
    method_id: int
    kb_id: int
    files: List[KBDataImportOne]


class TableAnalysisRequest(BaseModel):
    app_id: int
    chat_id: int
    uid: str
    file_hash: str
    file_url: str
