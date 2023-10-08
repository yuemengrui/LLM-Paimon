# *_*coding:utf-8 *_*
from fastapi import FastAPI
from . import chat, auth, appstore


def register_router(app: FastAPI):
    app.include_router(router=chat.router, prefix="", tags=["Chat"])
    # app.include_router(router=embedding.router, prefix="", tags=['Embedding'])
    app.include_router(router=auth.router, prefix="", tags=['Auth'])
    app.include_router(router=appstore.router, prefix="", tags=['App Store'])
