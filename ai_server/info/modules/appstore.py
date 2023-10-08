# *_*coding:utf-8 *_*
# @Author : YueMengRui
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from info.configs.base_configs import API_LIMIT
from info import logger, limiter, get_db
from fastapi.responses import JSONResponse
from info.utils.Authentication import verify_token
from info.models import App, ChatRecord, ChatMessageRecord
from .protocol import AppCreateRequest, ErrorResponse, AppChatListRequest, AppChatCreateRequest, AppChatMessageListRequest
from info.utils.response_code import RET, error_map

router = APIRouter()


@router.api_route(path='/ai/app/list', methods=['GET'], summary="app list")
@limiter.limit(API_LIMIT['auth'])
def get_app_list(request: Request, db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    app_list = db.query(App).filter(App.user_id == user_id, App.is_delete == False).order_by(App.update_time.desc()).all()

    return JSONResponse({'list': [x.to_dict() for x in app_list]})


@router.api_route(path='/ai/app/create', methods=['POST'], summary="app create")
@limiter.limit(API_LIMIT['auth'])
def app_create(app_create_req: AppCreateRequest, request: Request, db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    new_app = App()
    new_app.user_id = user_id
    new_app.name = app_create_req.name
    new_app.llm_name = app_create_req.llm_name

    try:
        db.add(new_app)
        db.commit()
    except Exception as e:
        logger.error({'DB ERROR': e})
        db.rollback()
        return JSONResponse(ErrorResponse(errcode=RET.DBERR, errmsg=error_map[RET.DBERR]).dict())

    return JSONResponse({'errcode': RET.OK, 'errmsg': error_map[RET.OK]})


@router.api_route(path='/ai/app/chat/list', methods=['POST'], summary="app chat list")
@limiter.limit(API_LIMIT['auth'])
def app_chat_list(req: AppChatListRequest, request: Request, db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    chat_list = db.query(ChatRecord).filter(ChatRecord.app_id == req.app_id, ChatRecord.is_delete == False).order_by(ChatRecord.update_time.desc()).all()

    return JSONResponse({'list': [x.to_dict() for x in chat_list]})


@router.api_route(path='/ai/app/chat/create', methods=['POST'], summary="app chat list")
@limiter.limit(API_LIMIT['auth'])
def app_chat_create(req: AppChatCreateRequest, request: Request, db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    new_chat = ChatRecord()
    new_chat.app_id = req.app_id
    new_chat.name = req.name

    try:
        db.add(new_chat)
        db.commit()
    except Exception as e:
        logger.error({'DB ERROR': e})
        db.rollback()
        return JSONResponse(ErrorResponse(errcode=RET.DBERR, errmsg=error_map[RET.DBERR]).dict())

    return JSONResponse({'errcode': RET.OK, 'errmsg': error_map[RET.OK]})


@router.api_route(path='/ai/app/chat/message/list', methods=['POST'], summary="app chat message list")
@limiter.limit(API_LIMIT['auth'])
def app_chat_message_list(req: AppChatMessageListRequest, request: Request, db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    message_list = db.query(ChatMessageRecord).filter(ChatMessageRecord.chat_id == req.chat_id, ChatMessageRecord.is_delete == False).order_by(ChatMessageRecord.create_time.desc()).all()[:10]

    return JSONResponse({'list': [x.to_dict() for x in message_list[::-1]]})




