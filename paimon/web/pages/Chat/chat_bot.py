# *_*coding:utf-8 *_*
# @Author : YueMengRui
import json
import streamlit as st
from typing import List
from api_servers import get_llm_answer


class HistoryTypes:

    def __init__(self, types: List[str]):
        for t in types:
            setattr(HistoryTypes, t, t)


class ChatBot:

    def __init__(
            self,
            user_avatar: str = "user",
            assistant_avatar: str = "assistant",
            greetings: str = f"欢迎使用 [`LLM-Paimon`](https://github.com/yuemengrui/LLM-Paimon.git)! 您可以开始提问了.",
    ):
        self._user_avatar = user_avatar
        self._assistant_avatar = assistant_avatar
        self._greetings = greetings
        self.history_types = HistoryTypes(['conversation', 'instruction', 'notice'])
        self.init_session_states()

    @property
    def model_history(self):
        if 'model_history' not in st.session_state:
            st.session_state.update({'model_history': []})

        return st.session_state.model_history

    @property
    def history(self):
        if 'history' not in st.session_state:
            st.session_state.update({'history': []})

        return st.session_state.history

    def add_history(self, role, content, history_type):
        self.history.append({
            "role": role,
            "content": content,
            "type": history_type
        })

    @staticmethod
    def reset_history():
        st.session_state.update({'history': []})

    def init_session_states(self):
        if not self.history:
            if self._greetings:
                self.add_history("assistant", self._greetings, self.history_types.notice)

    def display_conversation(self):
        for msg in self.history:
            avatar = self._user_avatar if msg["role"] == "user" else self._assistant_avatar
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg['content'])

    def user_say(self, prompt, history_type):
        with st.chat_message("user", avatar=self._user_avatar):
            st.markdown(prompt)

        self.add_history("user", prompt, history_type)

    def ai_say(self, prompt, history_type):
        with st.chat_message("assistant", avatar=self._assistant_avatar):
            st.markdown(prompt)

        self.add_history("assistant", prompt, history_type)

    def answer(self, prompt, history_type, model_name=None, history_len=10, generation_configs={}):
        if not isinstance(history_len, int):
            history_len = 10
        if history_len == 0:
            history = []
        else:
            history = self.model_history[-history_len:]

        with st.chat_message('assistant', avatar=self._assistant_avatar):
            message_placeholder = st.empty()
            for answer, _, usage in get_llm_answer(prompt, model_name, history=history,
                                                   generation_configs=generation_configs):
                text = f"{answer}  ▌\n\n{usage}"
                message_placeholder.markdown(text)
            text = text.replace('▌', '')
            message_placeholder.markdown(text)

        self.add_history("assistant", answer, history_type)
        self.model_history.append([prompt, answer])

    def export2json(self):
        return json.dumps(self.history, ensure_ascii=False, indent=2)
