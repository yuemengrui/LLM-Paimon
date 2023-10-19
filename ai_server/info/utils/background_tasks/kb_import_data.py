# *_*coding:utf-8 *_*
# @Author : YueMengRui
import os
from info import get_mysql_db, logger, milvus_db
from fastapi import Depends
from sqlalchemy.orm import Session
from info.utils.get_md5 import md5hex
from info.libs.Knowledge_Base.loader.file_loader import load_file
from info.utils.api_servers.llm_base import servers_embedding_text
from info.mysql_models import KnowledgeBase, KBData, KBDataDetail, FileSystem


def auto_chunk(req, mysql_db, emb_model_list):
    for emb_model in emb_model_list:
        logger.info(f'background task: {emb_model}')
        for fil in req.files:
            logger.info(f"background task: {fil.file_hash} import start......")
            file_system = mysql_db.query(FileSystem).filter(FileSystem.file_hash == fil.file_hash).first()
            if file_system is None:
                logger.error(f"background task: {fil.file_hash} import failed: file system query failed")
                continue

            local_file_path = os.path.join(file_system.base_dir, fil.file_hash[:2], fil.file_hash[2:4], fil.file_hash)

            if not os.path.exists(local_file_path):
                logger.error(
                    f"background task: {fil.file_hash} import failed: file local path {local_file_path} not exist")
                continue
            file_ext = fil.file_name.lower().split('.')[-1]
            docs = load_file(filepath=local_file_path, ext=file_ext)
            # for doc in docs:
            #     doc.metadata.update({'file_hash': fil.file_hash})
            sentences = [d.page_content for d in docs]
            texts = []
            text_hashs = []
            for sen in sentences:
                sen_hash = md5hex(sen.encode('utf-8'))
                if sen_hash != '' and sen_hash not in text_hashs:
                    texts.append(sen)
                    text_hashs.append(sen_hash)

            embedding_resp = servers_embedding_text(sentences=texts, model_name=emb_model)

            embeddings = embedding_resp.json()['data']['embeddings']

            if not milvus_db.upsert_data(collection_name=emb_model, texts=texts, text_hashs=text_hashs,
                                         embeddings=embeddings):
                logger.error(f"background task: {fil.file_hash} import failed: milvus insert data failed!!!")
                continue

            new_kb_data = KBData()
            new_kb_data.kb_id = req.kb_id
            new_kb_data.method_id = req.method_id
            new_kb_data.file_hash = fil.file_hash
            new_kb_data.file_name = fil.file_name
            new_kb_data.file_type = fil.file_type
            new_kb_data.file_size = fil.file_size
            new_kb_data.file_url = fil.file_url
            new_kb_data.data_total = len(texts)
            mysql_db.add(new_kb_data)
            mysql_db.flush()
            data_id = new_kb_data.id

            kb_data_detail_list = []
            for i in range(len(text_hashs)):
                new_data_detail = KBDataDetail()
                new_data_detail.data_id = data_id
                new_data_detail.content = texts[i]
                new_data_detail.content_hash = text_hashs[i]
                kb_data_detail_list.append(new_data_detail)

            mysql_db.add_all(kb_data_detail_list)
            try:
                mysql_db.commit()
                logger.info(f"background task: {fil.file_hash} import successful")
            except Exception as e:
                logger.error({'DB ERROR': e})
                mysql_db.rollback()


def import_data_2_kb(req, mysql_db):
    logger.info('background task import data start......')
    kb = mysql_db.query(KnowledgeBase).get(req.kb_id)
    if kb:
        emb_model_list = eval(kb.emb_model_list)
        if req.method_id == 1:
            auto_chunk(req, mysql_db, emb_model_list)
