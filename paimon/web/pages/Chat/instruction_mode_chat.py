# *_*coding:utf-8 *_*
# @Author : YueMengRui
from .base_chat import BaseChat
from api_servers import get_llm_name_list, get_embedding_model_name_list

INSTRUCTION_SET = ["@当前模型", "@切换大模型", "@切换embedding模型"]


class InstructionModeChat(BaseChat):

    def __init__(self):
        super().__init__()
        self.current_instruction = None
        self.prompt_template = "{}。改写前面这句话以不同的表述方式返回。"

    def in_instruction_chat(self, prompt):
        if self.current_instruction == '@切换大模型' or self.current_instruction == '@切换embedding模型':
            if 'embedding' in self.current_instruction:
                model_name_list = get_embedding_model_name_list()
                current_model_name = self.current_embedding_name
            else:
                model_name_list = get_llm_name_list()
                current_model_name = self.current_llm_name

            if prompt in current_model_name:
                self.chat_bot.answer(self.prompt_template.format(f"当前使用的模型已经是：{current_model_name}"),
                                     history_type=self.chat_bot.history_types.instruction,
                                     model_name=self.current_llm_name,
                                     history_len=0)
                self.instruction_mode = False
                self.current_instruction = None
                return

            for model in model_name_list:
                if prompt in model:
                    if 'embedding' in self.current_instruction:
                        self.current_embedding_name = model
                    else:
                        self.current_llm_name = model

                    self.chat_bot.answer(self.prompt_template.format(f"已切换到 {model} 模型"),
                                         history_type=self.chat_bot.history_types.instruction,
                                         model_name=self.current_llm_name,
                                         history_len=0)
                    self.instruction_mode = False
                    self.current_instruction = None
                    return

            self.chat_bot.answer(
                self.prompt_template.format(f"暂时不支持 {prompt} ，请选择支持的模型：{model_name_list}"),
                history_type=self.chat_bot.history_types.instruction, model_name=self.current_llm_name, history_len=0)
            return

        self.chat_bot.answer(self.prompt_template.format("抱歉，我暂时无法理解您的指令，可以再确切地告诉我一遍吗？"),
                             history_type=self.chat_bot.history_types.instruction, model_name=self.current_llm_name,
                             history_len=0)

    def get_instruction_chat(self, prompt):
        for inst in INSTRUCTION_SET:
            if inst.startswith(prompt):
                self.current_instruction = inst
                break

        if self.current_instruction == '@当前模型':
            self.instruction_mode = False
            self.current_instruction = None
            self.chat_bot.answer(self.prompt_template.format(
                f"当前使用的大模型: {self.current_llm_name}, 当前使用的embedding模型: {self.current_embedding_name}"),
                history_type=self.chat_bot.history_types.instruction, model_name=self.current_llm_name, history_len=0)
            return

        elif self.current_instruction == '@切换大模型' or self.current_instruction == '@切换embedding模型':
            if 'embedding' in self.current_instruction:
                if not self.current_embedding_name:
                    self.instruction_mode = False
                    self.current_instruction = None
                    self.chat_bot.answer(self.prompt_template.format("当前没有可用的embedding模型"),
                                         history_type=self.chat_bot.history_types.instruction,
                                         model_name=self.current_llm_name,
                                         history_len=0)
                    return
                model_name_list = get_embedding_model_name_list()
                current_model_name = self.current_embedding_name
            else:
                model_name_list = get_llm_name_list()
                current_model_name = self.current_llm_name

            if len(model_name_list) < 2:
                self.instruction_mode = False
                self.current_instruction = None
                self.chat_bot.answer(
                    self.prompt_template.format(f"当前使用的模型是：{current_model_name}, 没有其他模型可供选择"),
                    history_type=self.chat_bot.history_types.instruction,
                    model_name=self.current_llm_name,
                    history_len=0)
                return
            else:
                model_name_list.remove(current_model_name)
                self.chat_bot.answer(self.prompt_template.format(
                    f"当前使用的模型是：{current_model_name}, 可供选择的大模型有：{model_name_list}, 请问您想选择哪个模型呢？"),
                    history_type=self.chat_bot.history_types.instruction,
                    model_name=self.current_llm_name,
                    history_len=0)
                return

        self.chat_bot.answer(self.prompt_template.format("抱歉，我暂时无法理解您的指令，可以再确切地告诉我一遍吗？"),
                             history_type=self.chat_bot.history_types.instruction,
                             model_name=self.current_llm_name,
                             history_len=0)

    def instruction_mode_handler(self, prompt):
        if self.current_instruction:
            self.in_instruction_chat(prompt)
        else:
            if prompt == '@':
                self.chat_bot.ai_say("当前支持的指令：" + str(INSTRUCTION_SET),
                                     history_type=self.chat_bot.history_types.instruction)
                self.instruction_mode = False
            else:
                self.get_instruction_chat(prompt)
