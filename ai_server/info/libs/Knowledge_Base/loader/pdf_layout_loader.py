# *_*coding:utf-8 *_*
# @Author : YueMengRui
import cv2
import fitz
import base64
import requests
import numpy as np
from copy import deepcopy
from mylogger import logger
from configs import API_TABLE_ANALYSIS, API_OCR_GENERAL, API_LAYOUT_ANALYSIS


class PDFLayoutLoader:

    def table_analysis(self, image):
        try:
            res = requests.post(url=API_TABLE_ANALYSIS, json={'image': self.cv2_to_base64(image), 'with_ocr': True})
            return res.json()['data']
        except Exception as e:
            logger.error({'EXCEPTION': e})
            return []

    def cv2_to_base64(self, image):
        return base64.b64encode(np.array(cv2.imencode('.jpg', image)[1]).tobytes()).decode('utf-8')

    def ocr(self, image):
        try:
            res = requests.post(url=API_OCR_GENERAL, json={'image': self.cv2_to_base64(image)})
            return [x['text'][0] for x in res.json()['data']]
        except Exception as e:
            logger.error({'EXCEPTION': e})
            return []

    def get_layout(self, image, score_threshold=0.5):

        try:
            res = requests.post(url=API_LAYOUT_ANALYSIS, json={'image': self.cv2_to_base64(image)})
            return res.json()['data']
        except Exception as e:
            logger.error({'EXCEPTION': e})
            return []

    def merge_chunks(self, docs):
        all_pages = []
        for d in docs:
            chunks = []
            temp = []
            for i in d['page_content']:
                if i['label'] == 'title':
                    if len(temp) > 0:
                        chunks.append({'type': 'text', 'content': '\n'.join(deepcopy(temp))})
                        temp = []

                    if len(i['text'].strip()) > 0:
                        temp.append(i['text'].strip())
                elif i['label'] == 'table':
                    if len(temp) > 0:
                        chunks.append({'type': 'text', 'content': '\n'.join(deepcopy(temp))})
                        temp = []
                    del i['label']
                    chunks.append({'type': 'table', **i})
                elif i['label'] == 'figure':
                    if len(temp) > 0:
                        chunks.append({'type': 'text', 'content': '\n'.join(deepcopy(temp))})
                        temp = []
                    del i['label']
                    chunks.append({'type': 'figure', **i})
                else:
                    if len(i['text'].strip()) > 0:
                        temp.append(i['text'].strip())

            if len(temp) > 0:
                chunks.append({'type': 'text', 'content': '\n'.join(deepcopy(temp))})

            if len(chunks) > 0:
                all_pages.append({'page': d['page'], 'chunks': chunks})

        return all_pages

    def load(self, pdf_path: str):
        """
        :param pdf_path:
        :return: [{'page': 0, 'chunks': [
                                         {'type': 'text', 'content': ''},
                                         {'type': 'table', 'image': '', 'table_caption': '', 'table_cells':'', 'html':''},
                                         {'type': 'figure', 'image': '', 'figure_caption':''}
                                        ]
                  }
                ]
        """

        doc = fitz.open(pdf_path)

        doc_pages = doc.page_count

        docs = []
        for page in range(doc_pages):
            page_content = []
            try:
                zoom_x = 2.0
                zoom_y = 2.0
                trans = fitz.Matrix(zoom_x, zoom_y)
                pm = doc[page].get_pixmap(matrix=trans)
                image_bytes = pm.tobytes()
                image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
                layouts = self.get_layout(image)
            except Exception as e:
                logger.error({'EXCEPTION': e})
                continue

            start_y = 0
            end_y = image.shape[0]
            table_caption = ''
            figure_caption = ''
            for ind, lay in enumerate(layouts):
                if lay['label'] == 'header':
                    start_y = max(lay['box'][3], start_y)
                    continue
                elif lay['label'] == 'footer':
                    end_y = min(lay['box'][1], end_y)
                    continue
                else:
                    top_text_list = self.ocr(image[start_y:lay['box'][1], :])
                    if len(top_text_list) > 0:
                        page_content.append({'label': 'text', 'text': '\n'.join(top_text_list)})

                    if lay['label'] == 'directory':
                        page_content.append({'label': 'directory', 'text': ''})
                        start_y = lay['box'][3]
                    elif lay['label'] == 'title':
                        text_list = self.ocr(image[lay['box'][1]:lay['box'][3], lay['box'][0]:lay['box'][2]])
                        page_content.append({'label': 'title', 'text': ''.join(text_list)})
                        start_y = lay['box'][3]
                    elif lay['label'] == 'table_caption':
                        text_list = self.ocr(image[lay['box'][1]:lay['box'][3], lay['box'][0]:lay['box'][2]])
                        table_caption = ''.join(text_list)
                        start_y = lay['box'][3]
                    elif lay['label'] == 'table':
                        table_image = image[lay['box'][1]:lay['box'][3], lay['box'][0]:lay['box'][2]]
                        res = self.table_analysis(table_image)
                        if len(res) > 0:
                            pred_html = f"""<html><body><table border="1"><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><tr><td><table  border="1">{res['html'].replace('<html><body><table>', '').replace('</table></body></html>', '')}</table></td></tr></table></body></html>"""

                            page_content.append({'label': 'table', 'image': table_image, 'table_caption': table_caption,
                                                 'table_cells': res['table_cells'], 'html': pred_html})
                        start_y = lay['box'][3]

                    elif lay['label'] == 'figure_caption':
                        text_list = self.ocr(image[lay['box'][1]:lay['box'][3], lay['box'][0]:lay['box'][2]])
                        figure_caption = ''.join(text_list)
                        start_y = lay['box'][3]
                    elif lay['label'] == 'figure':
                        page_content.append({'label': 'figure',
                                             'image': image[lay['box'][1]:lay['box'][3], lay['box'][0]:lay['box'][2]],
                                             'figure_caption': figure_caption})
                        start_y = lay['box'][3]

            text_list = self.ocr(image[start_y:end_y, :])
            if len(text_list) > 0:
                page_content.append({'label': 'text', 'text': '\n'.join(text_list)})

            docs.append({'page': page + 1, 'page_content': page_content})

        docs = self.merge_chunks(docs)

        return docs
