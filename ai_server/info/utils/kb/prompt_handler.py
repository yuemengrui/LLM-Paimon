# *_*coding:utf-8 *_*
# @Author : YueMengRui
from info import logger, milvus_db
from info.configs.prompt_template import kb_qa_prompt_template
from info.mysql_models import App, KBData, KBDataDetail, KnowledgeBase
from info.utils.kb.MultiQueryRetriever import multiquery_retriever


def get_final_prompt(prompt, app_id, mysql_db):
    related_docs = []
    msg = {}
    app = mysql_db.query(App).get(app_id)

    data_chunk_map = {}
    if app and app.kb_id:
        text_hash_list = []
        embedding_model = None
        kb = mysql_db.query(KnowledgeBase).get(app.kb_id)
        if kb:
            embedding_model = eval(kb.emb_model_list)[0]
            kb_data_list = mysql_db.query(KBData).filter(KBData.kb_id == app.kb_id, KBData.is_delete == False).all()
            if kb_data_list:
                for kb_data in kb_data_list:
                    data_chunks = mysql_db.query(KBDataDetail).filter(KBDataDetail.data_id == kb_data.id).all()
                    if data_chunks:
                        for c in data_chunks:
                            data_chunk_map.update({c.content_hash: kb_data.to_dict()})
                            text_hash_list.append(c.content_hash)

        if all([text_hash_list, embedding_model]):
            if app.is_multiQueryRetriever_enabled:
                queries, docs, context = multiquery_retriever(prompt, embedding_model, list(set(text_hash_list)))
                temp_docs = {}
                for d in docs:
                    kb_dat = data_chunk_map[d['text_hash']]
                    if kb_dat['file_hash'] in temp_docs:
                        temp_docs[kb_dat['file_hash']]['related_texts'].append(d)
                    else:
                        kb_dat.update({'related_texts': [d]})
                        temp_docs.update({kb_dat['file_hash']: kb_dat})

                related_docs = list(temp_docs.values())
                msg.update({"MultiQueryRetriever": {"queries": queries}})
                prompt = kb_qa_prompt_template.format(query=prompt, context=context)

    return prompt, related_docs, msg
