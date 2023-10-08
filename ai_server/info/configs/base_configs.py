# *_*coding:utf-8 *_*
# @Author : YueMengRui

FASTAPI_HOST = '0.0.0.0'
FASTAPI_PORT = 10000

SECRET_KEY = 'llm-paimon'
TOKEN_EXPIRES = 12 * 60 * 60

USERNAME_FILTER = ['administer', 'administrator']

################
LLM_SERVER_PREFIX = ''
LLM_SERVER_APIS = {
    'model_list': LLM_SERVER_PREFIX + '/ai/llm/list',
    'token_counter': LLM_SERVER_PREFIX + '/ai/llm/token_count',
    'chat': LLM_SERVER_PREFIX + '/ai/llm/chat'
}
################

# API LIMIT
API_LIMIT = {
    "auth": "120/minute",
    "model_list": "120/minute",
    "chat": "15/minute",
    "token_count": "60/minute",
    "text_embedding": "60/minute",
}
