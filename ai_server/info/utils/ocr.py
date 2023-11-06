# *_*coding:utf-8 *_*
# @Author : YueMengRui
import numpy as np
import cv2
import requests
import base64
from mylogger import logger
from configs import API_OCR_BYTE, API_OCR_GENERAL


def get_ocr_byte_res(img):
    data = {
        'file': np.array(cv2.imencode('.jpg', img)[1]).tobytes()
    }

    try:
        res = requests.post(url=API_OCR_BYTE,
                            files=data)
        txt = res.json()['data']['results']
    except Exception as e:
        logger.error({'EXCEPTION': e})
        txt = ''

    return txt


def get_ocr_general_res(img):
    data = {
        'image': base64.b64encode(np.array(cv2.imencode('.png', img)[1]).tobytes()).decode()
    }

    try:
        res = requests.post(url=API_OCR_GENERAL,
                            json=data)

        txt_list = res.json()['data']['results']
        txt_list = [x['text'][0] for x in txt_list]
        txt = ''.join(txt_list)
        return txt
    except Exception as e:
        logger.error({'EXCEPTION': e})
        return ''
