# *_*coding:utf-8 *_*
# @Author : YueMengRui
import os
import streamlit as st
from web.pages.Chat.chat import chat
from web.pages.instructionSet import instruction_set
from streamlit_option_menu import option_menu

if __name__ == '__main__':

    st.set_page_config(
        page_title="LLM-Paimon WebUI",
        page_icon="random",
        initial_sidebar_state="auto",
        menu_items={
            'Get Help': 'https://github.com/yuemengrui/LLM-Paimon.git',
            'Report a bug': "https://github.com/yuemengrui/LLM-Paimon.git/issues",
            'About': f"""欢迎使用 LLM-Paimon WebUI V1 ！"""
        }
    )

    pages = {
        "对话": {
            "icon": "wechat",
            "func": chat.page,
        },
        "Paimon指令集": {
            "icon": "cpu",
            "func": instruction_set.page,
        },
    }

    with st.sidebar:
        title_img, title = st.columns(2)
        with title_img:
            st.image(os.path.join("web/resources", "images", "paimon.jpg"),
                     use_column_width=True
                     )
        with title:
            st.title(":blue[LLM-Paimon WebUI] :grin:", anchor="YueMengRui")

        st.caption(
            f"""<p align="right">当前版本：V1</p>""",
            unsafe_allow_html=True,
        )
        options = list(pages)
        icons = [x["icon"] for x in pages.values()]

        default_index = 0
        selected_page = option_menu(
            "",
            options=options,
            icons=icons,
            menu_icon="chat-quote",
            default_index=default_index,
        )

    if selected_page in pages:
        pages[selected_page]["func"]()
