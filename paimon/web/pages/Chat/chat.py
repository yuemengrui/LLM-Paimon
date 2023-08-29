# *_*coding:utf-8 *_*
# @Author : YueMengRui
import datetime
import streamlit as st
from .instruction_mode_chat import InstructionModeChat


class Chat(InstructionModeChat):

    def page(self):
        self.chat_bot.init_session_states()
        self.chat_bot.display_conversation()

        chat_input_placeholder = "请输入对话内容，换行请使用Ctrl+Enter "

        if prompt := st.chat_input(chat_input_placeholder, key="prompt", max_chars=32 * 1024):
            if self.current_llm_name:
                self.chat_bot.user_say(prompt, history_type=self.chat_bot.history_types.conversation)
                if prompt.startswith('@') or self.instruction_mode:
                    if not self.instruction_mode:
                        self.instruction_mode = True
                        st.toast("指令模式已启动")
                    self.instruction_mode_handler(prompt)
                    if not self.instruction_mode:
                        st.toast("指令模式已关闭")
                else:
                    with st.spinner("正在思考..."):
                        self.chat_bot.answer(prompt, model_name=self.current_llm_name,
                                             history_type=self.chat_bot.history_types.conversation,
                                             history_len=self.history_len)

        with st.sidebar:
            cols = st.columns(2)
            export_btn = cols[0]
            if cols[1].button(
                    "清空对话",
                    use_container_width=True,
            ):
                self.chat_bot.reset_history()
                st.experimental_rerun()

        export_btn.download_button(
            "导出记录",
            self.chat_bot.export2json(),
            file_name=f"{datetime.datetime.now():%Y-%m-%d %H.%M}_对话记录.json",
            mime="application/json",
            use_container_width=True,
        )


chat = Chat()
