# *_*coding:utf-8 *_*
# @Author : YueMengRui
import json
import time
import requests
from sqlalchemy.orm import Session
from fastapi import APIRouter, Request, Depends
from info.utils.Authentication import verify_token
from info import logger, limiter, get_db
from info.configs.base_configs import API_LIMIT, LLM_SERVER_APIS
from .protocol import ChatRequest, TokenCountRequest, ErrorResponse
from fastapi.responses import JSONResponse, StreamingResponse
from info.models import ChatMessageRecord
from info.utils.response_code import RET, error_map

router = APIRouter()


@router.api_route(path='/ai/llm/list', methods=['GET'], summary="获取支持的llm列表")
@limiter.limit(API_LIMIT['model_list'])
def support_llm_list(request: Request, user_id=Depends(verify_token)):
    return requests.get(url=LLM_SERVER_APIS['model_list'])


@router.api_route('/ai/llm/chat', methods=['POST'], summary="Chat")
@limiter.limit(API_LIMIT['chat'])
def llm_chat(chat_req: ChatRequest, request: Request, db: Session = Depends(get_db), user_id=Depends(verify_token)):
    logger.info(str(chat_req.dict()) + ' user_id: {}'.format(user_id))
    start = time.time()
    new_message_user = ChatMessageRecord()
    new_message_user.chat_id = chat_req.chat_id
    new_message_user.uid = chat_req.uid
    new_message_user.role = 'user'
    new_message_user.content = chat_req.prompt
    new_message_user.llm_name = chat_req.model_name

    try:
        db.add(new_message_user)
        db.commit()
    except Exception as e:
        logger.error({'DB ERROR': e})
        db.rollback()
        return JSONResponse(ErrorResponse(errcode=RET.DBERR, errmsg=error_map[RET.DBERR]).dict())

    if chat_req.stream:
        resp = requests.post(url=LLM_SERVER_APIS['chat'], json=chat_req.dict(), stream=True)
        if 'event-stream' in resp.headers.get('content-type'):
            def stream_generate():
                for line in resp.iter_content(chunk_size=None):
                    yield line

                res = json.loads(line.decode('utf-8'))
                new_message_assistant = ChatMessageRecord()
                new_message_assistant.chat_id = chat_req.chat_id
                new_message_assistant.uid = chat_req.answer_uid
                new_message_assistant.role = 'assistant'
                new_message_assistant.content = res['answer']
                new_message_assistant.llm_name = res['model_name']
                new_message_assistant.response = res
                new_message_assistant.time_cost = f"{time.time() - start:.3f}s"

                try:
                    db.add(new_message_assistant)
                    db.commit()
                except Exception as e:
                    logger.error({'DB ERROR': e})
                    db.rollback()

            return StreamingResponse(stream_generate(), media_type="text/event-stream")
        else:
            return JSONResponse(resp.json())

    else:
        resp = requests.post(url=LLM_SERVER_APIS['chat'], json=chat_req.dict()).json()

        new_message_assistant = ChatMessageRecord()
        new_message_assistant.chat_id = chat_req.chat_id
        new_message_assistant.uid = chat_req.answer_uid
        new_message_assistant.role = 'assistant'
        new_message_assistant.content = resp['data']['answer']
        new_message_assistant.llm_name = resp['data']['model_name']
        new_message_assistant.response = resp['data']
        try:
            db.add(new_message_assistant)
            db.commit()
        except Exception as e:
            logger.error({'DB ERROR': e})
            db.rollback()
            return JSONResponse(ErrorResponse(errcode=RET.DBERR, errmsg=error_map[RET.DBERR]).dict())
        return JSONResponse(resp)


@router.api_route('/ai/llm/token_count', methods=['POST'], summary="token count")
@limiter.limit(API_LIMIT['token_count'])
def count_token(token_count_req: TokenCountRequest, request: Request):
    logger.info(str(token_count_req.dict()))

    return JSONResponse(requests.post(url=LLM_SERVER_APIS['token_counter'], json=token_count_req.json()).json())
