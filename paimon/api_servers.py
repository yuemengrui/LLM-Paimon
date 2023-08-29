# *_*coding:utf-8 *_*
# @Author : YueMengRui
import json
import hashlib
import requests
from configs import *


def md5hex(data):
    try:
        m = hashlib.md5()
        m.update(data)
        return str(m.hexdigest())
    except Exception as e:
        print(str({'EXCEPTION': e}) + '\n')
        return ''


def get_embedding_model_name_list():
    try:
        return requests.get(url=EMBEDDING_MODEL_NAME_LIST_URL).json()['data']['embedding_model_list']
    except:
        return []


def get_llm_name_list():
    try:
        return requests.get(url=LLM_MODEL_NAME_LIST_URL).json()['data']['llm_list']
    except:
        return []


def get_embeddings(sentences, model_name=None):
    data = {
        "model_name": model_name,
        "sentences": sentences
    }

    resp = requests.post(url=TEXT_EMBEDDING_URL, json=data)

    return resp.json()['data']['embeddings']


def get_llm_answer(prompt, model_name=None, history=[], generation_configs={}, stream=True):
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model_name": model_name,
        "prompt": prompt,
        "history": history,
        "generation_configs": generation_configs,
        "stream": stream
    }

    if stream:
        resp = requests.post(url=LLM_CHAT_URL, json=data, stream=True)
        for line in resp.iter_content(chunk_size=None):
            data = json.loads(line.decode("utf-8"))
            yield data['answer'], data['history'], data['usage']
    else:
        resp = requests.post(url=LLM_CHAT_URL, json=data, headers=headers, stream=False)
        return resp.json()['data']['history'], resp.json()['data']['usage']
