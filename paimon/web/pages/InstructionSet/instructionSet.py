# *_*coding:utf-8 *_*
# @Author : YueMengRui
import streamlit as st
from web.pages.Chat.instruction_mode_chat import INSTRUCTION_SET


class InstructionSet:

    def __init__(self):
        self.instruction_set = INSTRUCTION_SET

    def page(self):
        s = ''
        for i, ins in enumerate(self.instruction_set):
            s += f'{i + 1}. {ins}\n'
        st.markdown(s)


instruction_set = InstructionSet()
