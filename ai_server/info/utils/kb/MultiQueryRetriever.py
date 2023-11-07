# *_*coding:utf-8 *_*
# @Author : YueMengRui
import re
import json
from mylogger import logger
from info import milvus_db
from info.utils.api_servers.llm_base import servers_llm_chat, servers_embedding_text
from configs.prompt_template import multiqueryretriever_prompt_template


def multiquery_retriever(query, model_name, text_hash_list):
    queries = [query]
    resp = servers_llm_chat(prompt=multiqueryretriever_prompt_template.format(query=query), model_name=model_name)
    logger.info(f"multiquery_retriever: {resp}")
    resp_json_data = None
    if resp:
        result = re.search(r"```json(.*?)```", resp, re.DOTALL)
        if result:
            try:
                resp_json_data = json.loads(result.group(1))
            except:
                pass

        if resp_json_data is None:
            result = re.search(r"{(.*?)}", resp, re.DOTALL)
            if result:
                try:
                    resp_json_data = json.loads('{' + result.group(1) + '}')
                except:
                    pass

    if resp_json_data:
        logger.info(f"multiquery_retriever: json: {resp_json_data}")

        for i in list(resp_json_data.values()):
            if i not in queries:
                queries.append(i)

    related_docs = []
    text_hash_filter = []
    for q in queries:
        embedding = servers_embedding_text(sentences=[q], model_name=model_name).json()['embeddings'][0]

        results = milvus_db.similarity_search(model_name, embedding, expr=f"text_hash in {text_hash_list}", threshold=0.85)

        for r in results:
            if r['text_hash'] not in text_hash_filter:
                text_hash_filter.append(r['text_hash'])
                related_docs.append(r)

    related_docs.sort(key=lambda x: x['score'], reverse=True)

    logger.info(f"multiquery_retriever: related docs: {related_docs}")
    front = []
    back = []
    flag = 'front'

    for doc in related_docs:
        if flag == 'front':
            front.append(doc['text'])
            flag = 'back'
        else:
            back.append(doc['text'])
            flag = 'front'

    context = '\n'.join(front + back)
    logger.info(f"multiquery_retriever: context: {context}")

    return queries, related_docs, context


