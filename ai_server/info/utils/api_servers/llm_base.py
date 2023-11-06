# *_*coding:utf-8 *_*
# @Author : YueMengRui
import requests
from typing import List
from configs import LLM_SERVER_APIS, EMBEDDING_SERVER_APIS


def servers_llm_chat(prompt, model_name: str = "", history: list = [], generation_configs: dict = {}):
    req_data = {
        "model_name": model_name,
        "prompt": prompt,
        "history": history,
        "generation_configs": generation_configs,
        "stream": False
    }
    resp = requests.post(url=LLM_SERVER_APIS['chat'], json=req_data)

    return resp.json()['data']['answer']


def servers_token_count(prompt: str, model_name: str = ""):
    req_data = {
        "model_name": model_name,
        "prompt": prompt
    }

    return requests.post(url=LLM_SERVER_APIS['token_counter'], json=req_data)


def servers_get_llm_list():
    return requests.get(url=LLM_SERVER_APIS['model_list'])


def servers_get_embedding_model_list():
    return requests.get(url=EMBEDDING_SERVER_APIS['model_list'])


def servers_embedding_text(sentences: List[str], model_name: str = ""):
    req_data = {
        "model_name": model_name,
        "sentences": sentences
    }

    return requests.post(url=EMBEDDING_SERVER_APIS['embedding_text'], json=req_data)
