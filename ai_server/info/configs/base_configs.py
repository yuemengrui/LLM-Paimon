# *_*coding:utf-8 *_*
# @Author : YueMengRui

FASTAPI_HOST = '0.0.0.0'
FASTAPI_PORT = 5000

PREFIX_API_LLM_BASE = 'http://127.0.0.1:5000'
API_LLM_MODEL_LIST = PREFIX_API_LLM_BASE + '/ai/llm/list'
API_LLM_CHAT = PREFIX_API_LLM_BASE + '/ai/llm/chat'
API_TOKEN_COUNT = PREFIX_API_LLM_BASE + '/ai/llm/token_count'
API_EMBEDDING_MODEL_LIST = PREFIX_API_LLM_BASE + '/ai/embedding/model/list'
API_TEXT_EMBEDDING = PREFIX_API_LLM_BASE + '/ai/embedding/text'

API_OCR_GENERAL = 'http://127.0.0.1:6000/ai/ocr/general'

# API LIMIT
API_LIMIT = {
    "model_list": "120/minute",
    "chat": "15/minute",
    "token_count": "60/minute",
    "text_embedding": "60/minute",
}
