# *_*coding:utf-8 *_*
# @Author : YueMengRui
import os

OCR_URL = 'http://127.0.0.1:6000/ai/ocr/general'

EMBEDDING_MODEL_NAME_LIST_URL = 'http:///ai/embedding/model/list'
TEXT_EMBEDDING_URL = 'http:///ai/embedding/text'

LLM_MODEL_NAME_LIST_URL = 'http:///ai/llm/list'
LLM_CHAT_URL = 'http:///ai/llm/chat'

VECTOR_STORE_ROOT_DIR = './VectorStores'

TEMP = './TEMP'

os.makedirs(VECTOR_STORE_ROOT_DIR, exist_ok=True)
os.makedirs(TEMP, exist_ok=True)

PROMPT_TEMPLATE = """你是一个出色的助手，助手会尊重找到的材料并参考材料来回答用户的问题。助手会给出专业的解释，但不会过度演绎，同时回答中不会暴露引用的材料，请直接回复答案。
用户的问题是：{query}
材料：
```
{context}
```
"""
