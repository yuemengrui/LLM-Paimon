# *_*coding:utf-8 *_*
# @Author : YueMengRui
import os

FASTAPI_TITLE = 'LLM_Paimon'
FASTAPI_HOST = '0.0.0.0'
FASTAPI_PORT = 10000

LOG_DIR = 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

UPLOAD_FILE_URL = 'http://127.0.0.1:10000/ai/file/upload/public'

########################
API_OCR_GENERAL = 'http://127.0.0.1:6000/ai/ocr/general'
API_TABLE_ANALYSIS = 'http://127.0.0.1:6000/ai/table/analysis'
API_LAYOUT_ANALYSIS = 'http://127.0.0.1:6000/ai/layout/analysis'
########################

########################
# Auth Configs
SECRET_KEY = 'LLM-PaiMon-YueMengRui'
USERNAME_FILTER = ['administer', 'administrator']
TOKEN_EXPIRES = 12 * 60 * 60  # token过期时间
########################

########################
# File System Configs
THIS_SERVER_URL = 'http://127.0.0.1:10000'  # 本服务地址
FILE_SYSTEM_DIR = './file_system'
TEMP = './temp'
os.makedirs(FILE_SYSTEM_DIR, exist_ok=True)
os.makedirs(TEMP, exist_ok=True)
########################

########################
# LLM Configs
LLM_SERVER_PREFIX = 'http://127.0.0.1:5000'  # LLM Server 地址
LLM_SERVER_APIS = {
    'model_list': LLM_SERVER_PREFIX + '/ai/llm/list',
    'token_counter': LLM_SERVER_PREFIX + '/ai/llm/token_count',
    'chat': LLM_SERVER_PREFIX + '/ai/llm/chat',
    'embedding_model_list': LLM_SERVER_PREFIX + '/ai/embedding/model/list',
    'embedding_text': LLM_SERVER_PREFIX + '/ai/embedding/text'
}
########################

QWENVL_CHAT = 'http://127.0.0.1:5000/ai/llm/chat/qwenvl'

########################
# Embedding Configs
EMBEDDING_SERVER_PREFIX = 'http://127.0.0.1:6000'  # Embedding Server 地址
EMBEDDING_SERVER_APIS = {
    'model_list': EMBEDDING_SERVER_PREFIX + '/ai/embedding/model/list',
    'embedding_text': EMBEDDING_SERVER_PREFIX + '/ai/embedding/text',
    'embedding_token_count': EMBEDDING_SERVER_PREFIX + '/ai/embedding/token/count',
}
########################

########################
# Mysql Configs
MYSQL_HOST = '127.0.0.1'
MYSQL_POST = 3306
MYSQL_USERNAME = ''
MYSQL_PASSWORD = ''
MYSQL_DATABASE_NAME = 'llm_paimon'
########################

########################
# Milvus Configs
MILVUS_HOST = '127.0.0.1'
MILVUS_PORT = 12006
MILVUS_DB_NAME = 'llm_paimon'
MILVUS_USERNAME = ''
MILVUS_PASSWORD = ''
########################

SYSTEM_APP_LIST = ['tableQA', '图文理解']
########################
# API LIMIT Configs
API_LIMIT = {
    "auth": "120/minute",
    "model_list": "120/minute",
    "chat": "15/minute",
    "token_count": "60/minute",
    "text_embedding": "60/minute",
}
########################
