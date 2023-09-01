# *_*coding:utf-8 *_*
# @Author : YueMengRui
import datetime
import os
import time
import json
import shutil
import webbrowser
import pandas as pd
import streamlit as st
from typing import Dict, Tuple, Literal
from st_aggrid import AgGrid, JsCode
from configs import VECTOR_STORE_ROOT_DIR, TEMP
from api_servers import get_embedding_model_name_list, md5hex
from knowledge_base import knowledge_vector_store
from st_aggrid.grid_options_builder import GridOptionsBuilder


def config_aggrid(
        df: pd.DataFrame,
        columns: Dict[Tuple[str, str], Dict] = {},
        selection_mode: Literal["single", "multiple", "disabled"] = "single",
        use_checkbox: bool = False,
) -> GridOptionsBuilder:
    gb = GridOptionsBuilder.from_dataframe(df)
    for (col, header), kw in columns.items():
        gb.configure_column(col, header, wrapHeaderText=True, **kw)
    gb.configure_selection(
        selection_mode=selection_mode,
        use_checkbox=use_checkbox,
        # pre_selected_rows=st.session_state.get("selected_rows", [0]),
    )
    return gb


class Knowledge:

    def __init__(self):
        self.vector_store_root_dir = VECTOR_STORE_ROOT_DIR
        self.current_embedding_name = None
        self.selected_kb = None
        if current_embedding_name := get_embedding_model_name_list():
            self.current_embedding_name = current_embedding_name[0]

        if self.get_kb_list():
            self.selected_kb = self.get_kb_list()[0]

    def load_files_info(self):
        if self.vector_store_root_dir and self.current_embedding_name and self.selected_kb:
            with open(os.path.join(self.vector_store_root_dir, self.current_embedding_name, self.selected_kb,
                                   'files_info.json'), 'r') as f:
                return json.load(f)

        return {}

    def save_files_info(self, data):
        with open(os.path.join(self.vector_store_root_dir, self.current_embedding_name, self.selected_kb,
                               'files_info.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_kb_list(self):
        try:
            return os.listdir(os.path.join(self.vector_store_root_dir, self.current_embedding_name))
        except Exception as e:
            print(e)
            return []

    def page(self):
        embedding_model = st.radio(
            "Embedding Models",
            [f":rainbow[{i}]" for i in get_embedding_model_name_list()],
            index=0,
            horizontal=True)

        if embedding_model:
            self.current_embedding_name = embedding_model[embedding_model.index('[') + 1:-1]

        kb_list = self.get_kb_list()
        selected_kb = st.selectbox(
            "请选择或新建知识库：",
            kb_list + ["新建知识库"],
            index=0
        )

        if selected_kb == "新建知识库":
            with st.form("新建知识库"):
                kb_name = st.text_input(
                    "新建知识库名称",
                    placeholder="新知识库名称",
                    key="kb_name",
                )

                submit_create_kb = st.form_submit_button(
                    "新建",
                    use_container_width=True,
                )

                if submit_create_kb:
                    if not kb_name or not kb_name.strip():
                        st.error(f"知识库名称不能为空！")
                    elif kb_name in kb_list:
                        st.error(f"名为 {kb_name} 的知识库已经存在！")
                    else:
                        os.makedirs(os.path.join(self.vector_store_root_dir, self.current_embedding_name, kb_name),
                                    exist_ok=True)

                        with open(os.path.join(self.vector_store_root_dir, self.current_embedding_name, kb_name,
                                               'files_info.json'), 'w') as f:
                            json.dump({}, f)

                    st.experimental_rerun()
        elif selected_kb:
            self.selected_kb = selected_kb
            files_info = self.load_files_info()
            # 上传文件
            # sentence_size = st.slider("文本入库分句长度限制", 1, 1000, SENTENCE_SIZE, disabled=True)
            files = st.file_uploader("上传知识文件",
                                     accept_multiple_files=True,
                                     )

            cols = st.columns(4)
            if cols[0].button(
                    "添加文件到知识库",
                    # help="请先上传文件，再点击添加",
                    # use_container_width=True,
                    disabled=len(files) == 0,
            ):
                for f in files:
                    temp_file = os.path.join(TEMP, f.name)

                    file_data = f.read()

                    with open(temp_file, 'wb') as ff:
                        ff.write(file_data)

                    file_hash = md5hex(file_data)
                    if file_hash not in files_info:
                        vector_dir = os.path.join(self.vector_store_root_dir, self.current_embedding_name, selected_kb)

                        if not knowledge_vector_store.build_vector_store(file_path=temp_file,
                                                                         file_hash=file_hash,
                                                                         vector_dir=vector_dir,
                                                                         embedding_model_name=self.current_embedding_name):
                            st.toast("失败", icon="✖")
                        else:
                            files_info.update({file_hash: {'file_hash': file_hash, 'file_name': f.name,
                                                           'upload_time': datetime.datetime.now().strftime(
                                                               '%Y-%m-%d %H:%M:%S')}})
                            self.save_files_info(files_info)

                    st.toast("成功", icon="✔")

                    shutil.rmtree(temp_file, ignore_errors=True)

            if cols[3].button(
                    "删除知识库",
                    use_container_width=True,
            ):
                shutil.rmtree(os.path.join(self.vector_store_root_dir, self.current_embedding_name, selected_kb))
                st.toast("成功")
                time.sleep(1)
                st.experimental_rerun()

            st.divider()

            # 知识库详情
            # st.info("请选择文件，点击按钮进行操作。")
            doc_details = pd.DataFrame([v for v in files_info.values()])
            if not len(doc_details):
                st.info(f"知识库 `{selected_kb}` 中暂无文件")
            else:
                st.write(f"知识库 `{selected_kb}` 中已有文件:")
                # doc_details.drop(columns=["kb_name"], inplace=True)
                doc_details = doc_details[["file_name", "upload_time", "file_hash"]]
                #     # doc_details["in_folder"] = doc_details["in_folder"].replace(True, "✓").replace(False, "×")
                #     # doc_details["in_db"] = doc_details["in_db"].replace(True, "✓").replace(False, "×")
                gb = config_aggrid(
                    doc_details,
                    {
                        ("file_name", "文档名称"): {},
                        ("upload_time", "上传时间"): {},
                        ("file_hash", "文件hash"): {}
                    },
                    "multiple",
                )

                doc_grid = AgGrid(
                    doc_details,
                    gb.build(),
                    theme="alpine",
                    custom_css={
                        "#gridToolBar": {"display": "none"},
                    },
                    allow_unsafe_jscode=True
                )

                selected_rows = doc_grid.get("selected_rows", [])

                cols = st.columns(4)

                if selected_rows:

                    if cols[0].button('查看文档分句详情',
                                      use_container_width=True):
                        st.divider()
                        sentences = knowledge_vector_store.get_doc_info(
                            os.path.join(self.vector_store_root_dir, self.current_embedding_name, selected_kb,
                                         selected_rows[0]['file_hash']))

                        for s in sentences:
                            st.markdown(s)

                    if cols[3].button(
                            "从知识库中删除",
                            type="primary",
                            use_container_width=True,
                    ):
                        for row in selected_rows:
                            files_info.pop(row['file_hash'])
                            st.toast(f"删除{row['file_name']}成功")

                        self.save_files_info(files_info)
                        time.sleep(1)
                        st.experimental_rerun()


knowledge = Knowledge()
