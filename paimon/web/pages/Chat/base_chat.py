# *_*coding:utf-8 *_*
# @Author : YueMengRui
from .chat_bot import ChatBot
from api_servers import get_llm_name_list, get_embedding_model_name_list


class BaseChat:

    def __init__(self):
        self.chat_bot = ChatBot(assistant_avatar="web/resources/images/paimon.jpg")
        self.instruction_mode = False
        self.current_llm_name = None
        self.current_embedding_name = None
        self.history_len = 0
        self.knowledge_chat = True
        llm_name_list = get_llm_name_list()
        if not llm_name_list:
            self.chat_bot.ai_say("当前没有大模型可用，无法为您提供服务", history_type=self.chat_bot.history_types.notice)
        else:
            self.current_llm_name = llm_name_list[0]

        embedding_name_list = get_embedding_model_name_list()
        if embedding_name_list:
            self.current_embedding_name = embedding_name_list[0]

