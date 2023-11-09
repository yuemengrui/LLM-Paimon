# *_*coding:utf-8 *_*
# @Author : YueMengRui
from fastapi import APIRouter, Request, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from configs import API_LIMIT
from info import logger, limiter, get_mysql_db, milvus_db
from fastapi.responses import JSONResponse
from info.utils.Authentication import verify_token
from info.mysql_models import KnowledgeBase, KBData
from .protocol import ErrorResponse, KBCreateRequest, KBDataImportRequest, KBDeleteRequest, KBDataListRequest
from info.utils.response_code import RET, error_map
from info.utils.api_servers.llm_base import servers_embedding_text
from info.utils.background_tasks.kb_import_data import import_data_2_kb

router = APIRouter()


@router.api_route(path='/ai/knowledge_base/list', methods=['GET'], summary="knowledge base list")
@limiter.limit(API_LIMIT['auth'])
def get_kb_list(request: Request,
                mysql_db: Session = Depends(get_mysql_db),
                user_id: int = Depends(verify_token)
                ):
    kb_list = mysql_db.query(KnowledgeBase).filter(KnowledgeBase.user_id == user_id,
                                                   KnowledgeBase.is_delete == False).order_by(
        KnowledgeBase.update_time.desc()).all()

    return JSONResponse({'list': [x.to_dict() for x in kb_list]})


@router.api_route(path='/ai/knowledge_base/create', methods=['POST'], summary="knowledge_base create")
@limiter.limit(API_LIMIT['auth'])
def kb_create(request: Request,
              req: KBCreateRequest,
              mysql_db: Session = Depends(get_mysql_db),
              user_id: int = Depends(verify_token)
              ):
    logger.info(str(req.dict()))
    new_kb = KnowledgeBase()
    new_kb.user_id = user_id
    new_kb.name = req.name
    new_kb.emb_model_list = str(req.embedding_model_list)

    try:
        mysql_db.add(new_kb)
        mysql_db.commit()
    except Exception as e:
        logger.error({'DB ERROR': e})
        mysql_db.rollback()
        return JSONResponse(ErrorResponse(errcode=RET.DBERR, errmsg=error_map[RET.DBERR]).dict(), status_code=500)

    return JSONResponse({'msg': error_map[RET.OK]})


@router.api_route(path='/ai/knowledge_base/delete', methods=['POST'], summary="knowledge_base create")
@limiter.limit(API_LIMIT['auth'])
def kb_delete(request: Request,
              req: KBDeleteRequest,
              mysql_db: Session = Depends(get_mysql_db),
              user_id: int = Depends(verify_token)
              ):
    logger.info(str(req.dict()) + ' user_id: ' + str(user_id))

    mysql_db.query(KnowledgeBase).filter(KnowledgeBase.id == req.kb_id, KnowledgeBase.user_id == user_id).update(
        {'is_delete': True})
    try:
        mysql_db.commit()
    except Exception as e:
        logger.error({'DB ERROR': e})
        mysql_db.rollback()
        return JSONResponse(ErrorResponse(errcode=RET.DBERR, errmsg=error_map[RET.DBERR]).dict(), status_code=500)

    return JSONResponse({'msg': error_map[RET.OK]})


@router.api_route(path='/ai/knowledge_base/data/list', methods=['POST'], summary="knowledge_base data list")
@limiter.limit(API_LIMIT['auth'])
def kb_data_list(request: Request,
                 req: KBDataListRequest,
                 mysql_db: Session = Depends(get_mysql_db),
                 user_id: int = Depends(verify_token)
                 ):
    logger.info(str(req.dict()) + ' user_id: ' + str(user_id))

    data_list = mysql_db.query(KBData).filter(KBData.kb_id == req.kb_id, KBData.is_delete == False).order_by(
        KBData.create_time.desc()).all()

    return JSONResponse({'list': [x.to_dict() for x in data_list]})


@router.api_route(path='/ai/knowledge_base/data/import', methods=['POST'], summary="knowledge_base import data")
@limiter.limit(API_LIMIT['auth'])
def kb_data_import(request: Request,
                   req: KBDataImportRequest,
                   background_tasks: BackgroundTasks,
                   mysql_db: Session = Depends(get_mysql_db),
                   user_id: int = Depends(verify_token)
                   ):
    logger.info(str(req.dict()))

    background_tasks.add_task(import_data_2_kb, req, mysql_db)

    return JSONResponse({'msg': error_map[RET.OK]})


@router.api_route(path='/ai/knowledge_base/test', methods=['POST'], summary="knowledge_base import data")
@limiter.limit(API_LIMIT['auth'])
async def kb_data_import(request: Request,
                         mysql_db: Session = Depends(get_mysql_db),
                         ):
    res = await request.json()
    logger.info(res)

    prompt = res['prompt']
    model_name = res['model_name']

    embedding_resp = servers_embedding_text(sentences=[prompt], model_name=model_name)

    embedding = embedding_resp.json()['embeddings'][0]

    hash_list = ['6ac87e9e2774b4f96988eab5abad3d14', 'e6aade6cd38ba0b4ad45d6c7ba6ecf13']
    milvus_db.similarity_search(model_name, embedding, expr=f"text_hash in {hash_list}")

    return JSONResponse({'msg': error_map[RET.OK]})
