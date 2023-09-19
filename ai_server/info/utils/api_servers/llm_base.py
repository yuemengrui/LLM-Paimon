# *_*coding:utf-8 *_*
# @Author : YueMengRui
from info.configs.base_configs import *
from typing import List
from info import logger

import requests


def servers_llm_chat(prompt: str, model_name: str = "", history: List = [], generation_configs: dict = {}, stream: bool = True):
    req_data = {
        "model_name": model_name,
        "prompt": prompt,
        "history": history,
        "generation_configs": generation_configs,
        "stream": stream
    }

    if stream:
        def stream_chat():
            response =  requests.post(url=API_LLM_CHAT, json=req_data)
            for chunk in response.iter_content(chunk_size=None):
                yield chunk.decode('utf-8')

        return stream_chat()

    else:
        response = requests.post(url=API_LLM_CHAT, json=req_data)
        return response


def servers_token_count(prompt:str, model_name: str = ""):
    req_data = {
        "model_name": model_name,
        "prompt": prompt
    }

    response = requests.post(url=API_TOKEN_COUNT, json=req_data)

    return response.json()


def servers_get_llm_list():
    response = requests.get(url=API_LLM_MODEL_LIST)
    try:
        return response.json()['data']['mode_list']
    except:
        logger.info(f"get llm list error: {response.text}")
        return []


def servers_get_embedding_model_list():
    response = requests.get(url=API_EMBEDDING_MODEL_LIST)
    try:
        return response.json()['data']['mode_list']
    except:
        logger.info(f"get embedding model list error: {response.text}")
        return []


def servers_embedding_text(sentences: List[str], model_name: str = ""):
    req_data = {
        "model_name": model_name,
        "sentences": sentences
    }

    response = requests.post(url=API_TEXT_EMBEDDING, json=req_data)

    return response.json()






