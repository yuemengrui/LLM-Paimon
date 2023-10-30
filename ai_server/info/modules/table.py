# *_*coding:utf-8 *_*
# @Author : YueMengRui
import os
import cv2
import json
import time
import requests
from sqlalchemy.orm import Session
from fastapi import APIRouter, Request, Depends
from info.utils.Authentication import verify_token
from info import logger, limiter, get_mysql_db
from info.configs.base_configs import API_LIMIT, LLM_SERVER_APIS
from .protocol import ChatRequest, TableAnalysisRequest, ErrorResponse
from fastapi.responses import JSONResponse, StreamingResponse
from info.mysql_models import ChatMessageRecord, ChatRecord, FileSystem
from info.utils.response_code import RET, error_map
from info.utils.box_segmentation import get_box
from info.utils.kb.prompt_handler import get_final_prompt
from info.utils.api_servers.llm_base import servers_get_llm_list
from info.utils.ocr import get_ocr_byte_res

router = APIRouter()


@router.api_route(path='/ai/table/analysis', methods=['POST'], summary="table analysis")
@limiter.limit(API_LIMIT['chat'])
def table_analysis(request: Request,
                   req: TableAnalysisRequest,
                   mysql_db: Session = Depends(get_mysql_db),
                   user_id=Depends(verify_token)
                   ):
    file = mysql_db.query(FileSystem).filter(FileSystem.file_hash == req.file_hash).first()
    if file:
        file_path = os.path.join(file.base_dir, file.file_hash[:2], file.file_hash[2:4], file.file_hash)

    origin_image = cv2.imread(file_path)

    try:
        origin_img, boxes = get_box(origin_image)
    except Exception as e:
        logger.error({'EXCEPTION': e})
        return JSONResponse(ErrorResponse(errcode=RET.SERVERERR, errmsg=error_map[RET.SERVERERR]).dict())

    table = []
    for box in boxes:
        crop_img = origin_img[box[1]:box[3], box[0]:box[2]]
        ocr_res = get_ocr_byte_res(crop_img)
        table.append({'box': box, 'text': ocr_res})

    return JSONResponse({'table': table})


# @router.api_route('/ai/llm/chat', methods=['POST'], summary="Chat")
# @limiter.limit(API_LIMIT['chat'])
# def llm_chat(request: Request,
#              req: ChatRequest,
#              mysql_db: Session = Depends(get_mysql_db),
#              user_id=Depends(verify_token)
#              ):
#     logger.info(str(req.dict()) + ' user_id: {}'.format(user_id))
#     start = time.time()
#     new_message_user = ChatMessageRecord()
#     new_message_user.chat_id = req.chat_id
#     new_message_user.uid = req.uid
#     new_message_user.role = 'user'
#     new_message_user.content = req.prompt
#     new_message_user.llm_name = req.model_name
#
#     chat = mysql_db.query(ChatRecord).get(req.chat_id)
#     if not chat.name:
#         chat.dynamic_name = req.prompt[:8]
#
#     try:
#         mysql_db.add(new_message_user)
#         mysql_db.commit()
#     except Exception as e:
#         logger.error({'DB ERROR': e})
#         mysql_db.rollback()
#         return JSONResponse(ErrorResponse(errcode=RET.DBERR, errmsg=error_map[RET.DBERR]).dict())
#
#     prompt, related_docs, msg = get_final_prompt(prompt=req.prompt, app_id=req.app_id, mysql_db=mysql_db)
#     logger.info(f"prompt: {prompt}")
#     req_data = {
#         "model_name": req.model_name,
#         "prompt": prompt,
#         "history": req.history,
#         "generation_configs": req.generation_configs,
#         "stream": False
#     }
#     if req.stream:
#         req_data.update({"stream": True})
#         resp = requests.post(url=LLM_SERVER_APIS['chat'], json=req_data, stream=True)
#         if 'event-stream' in resp.headers.get('content-type'):
#             def stream_generate():
#                 for line in resp.iter_content(chunk_size=None):
#                     res = json.loads(line.decode('utf-8'))
#                     res['time_cost'].update({'total': f"{time.time() - start:.3f}s"})
#                     retrieval = {}
#                     retrieval.update({'sources': related_docs})
#                     retrieval.update({'sources_len': sum([len(x['related_texts']) for x in related_docs])})
#                     retrieval.update(msg)
#                     res.update({'retrieval': retrieval})
#                     yield f"data: {json.dumps(res, ensure_ascii=False)}\n\n"
#
#                 new_message_assistant = ChatMessageRecord()
#                 new_message_assistant.chat_id = req.chat_id
#                 new_message_assistant.uid = req.answer_uid
#                 new_message_assistant.role = 'assistant'
#                 new_message_assistant.content = res['answer']
#                 new_message_assistant.llm_name = res['model_name']
#                 new_message_assistant.response = res
#                 if 'MultiQueryRetriever' in msg:
#                     new_message_assistant.is_multiQueryRetriever_enabled = True
#
#                 mysql_db.add(new_message_assistant)
#
#                 try:
#                     mysql_db.commit()
#                 except Exception as e:
#                     logger.error({'DB ERROR': e})
#                     mysql_db.rollback()
#
#             return StreamingResponse(stream_generate(), media_type="text/event-stream")
#         else:
#             return JSONResponse(resp.json())
#
#     else:
#         resp = requests.post(url=LLM_SERVER_APIS['chat'], json=req_data).json()['data']
#         resp['time_cost'].update({'total': f"{time.time() - start:.3f}s"})
#         retrieval = {}
#         retrieval.update({'sources': related_docs})
#         retrieval.update(msg)
#         resp.update({'retrieval': retrieval})
#
#         new_message_assistant = ChatMessageRecord()
#         new_message_assistant.chat_id = req.chat_id
#         new_message_assistant.uid = req.answer_uid
#         new_message_assistant.role = 'assistant'
#         new_message_assistant.content = resp['answer']
#         new_message_assistant.llm_name = resp['model_name']
#         new_message_assistant.response = resp
#         if 'MultiQueryRetriever' in msg:
#             new_message_assistant.is_multiQueryRetriever_enabled = True
#
#         mysql_db.add(new_message_assistant)
#
#         try:
#             mysql_db.commit()
#         except Exception as e:
#             logger.error({'DB ERROR': e})
#             mysql_db.rollback()
#             return JSONResponse(ErrorResponse(errcode=RET.DBERR, errmsg=error_map[RET.DBERR]).dict())
#         return JSONResponse(resp)
