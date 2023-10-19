# *_*coding:utf-8 *_*
# @Author : YueMengRui
""
kb_qa_prompt_template = """你是一个出色的文档问答助手，根据给定的文本片段和问题进行回答，仔细分析和思考每个文本片段的内容，回答要合理、简洁，直接回复答案，回复语言采用中文。
使用下面的文本片段列表，回答问题：{query}
```
{context}
```
"""

# context:
# 文本片段1: xxx
# 文本片段2: xxx

"""你是文字提取器，你要结构化的提取用户描述中的年份、省、市信息,没有年份、省、市信息信息则使用空值("")代替。
年份 (year) 指：用户输入中有含义的年份信息，如：2022、2021、""等
省 (province)：用户输入中有含义的省一级信息，如：云南省、山西省、""等
市(city)：用户输入中有含义的市一级信息，如：昆明市、成都市、""等
只能输出JSON格式，输出完毕后结束，不要生成新的用户输入，不要增加额外内容

示例：
用户输入：2022年上海市蝗虫的发生情况。
json: {"year" : "2022", "province":"上海市", "city": "上海市"}

用户输入：2022年昆明市病虫情报第1期。
json: {"year":"2022", "province":"云南省", "city"："昆明市"}

用户输入：蝗虫的发生情况。
json: {"year":"", "province":"", "city": ""}

请根据以下文本，按照模版输出内容。
用户输入：2022年昆明市小春粮食作物的情况
"""

"""
你是一个出色的助手，你需要判断给定的文本片段和用户的问题之间的关联性，仔细分析和思考用户的问题和下面每个文本片段的内容，将文本片段按照关联性从高到低重新排序，并去掉你认为不相关的文本片段，只返回排序后的文本片段列表。
用户的问题是：{query}
文本片段列表：
```
{context}
```
"""

"""
这是一个文本纠错任务，找出并纠正给定文本中的错误，如错字、错词等等，只返回纠正后的文本。
给定文本：{query}
"""

multiqueryretriever_prompt_template = "分析输入的问题，从多种角度生成最多5个相似问题，并以json形式输出结果，其中包括以下json key:question1,question2,question3,question4,question5。只返回json输出，不要返回非json内容。输入问题是：{query}"
