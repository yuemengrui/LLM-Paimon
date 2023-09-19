# *_*coding:utf-8 *_*
# @Author : YueMengRui
# *_*coding:utf-8 *_*
import time
from info.configs import *
from fastapi import FastAPI
from info.utils.logger import MyLogger
from starlette.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


limiter = Limiter(key_func=lambda *args, **kwargs: '127.0.0.1')
app = FastAPI(title="LLM_Paimon")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

logger = MyLogger()


@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"start request {request.method} {request.url.path}")
    start = time.time()

    response = await call_next(request)

    cost = time.time() - start
    logger.info(f"end request {request.method} {request.url.path} {cost:.3f}s")
    return response

from info.libs.Knowledge_Base.local_knowledge_handlers.local_knowledge_vector_store import KnowledgeVectorStore

knowledge_vector_store = KnowledgeVectorStore(logger=logger)

from info.modules import register_router

register_router(app)
