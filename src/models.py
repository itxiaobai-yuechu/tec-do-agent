# -*- coding: utf-8 -*-
"""
Get model client from model name
"""

import json

import colorama
import gradio as gr
from loguru import logger

from src import config
from src.base_model import ModelType
from src.utils import (
    hide_middle_chars,
    i18n,
)
from src.openai_client import OpenAIClient
from config import conf
from src.openai_client import AzureOpenAIClient


def get_help_model(
        model_name: str,
        user_name: str,
):
    model_type = ModelType.get_type(model_name)
    model = None
    try:
        if model_type == ModelType.OpenAI:
            logger.info(f"正在加载OpenAI模型: {model_name}")
            model = OpenAIClient(
                user_name=user_name,
                model_name=model_name,
                api_key=conf.get("help_model.api_key", ""),
                base_url=conf.get("help_model.base_url", ""),
            )
        # elif model_type == ModelType.OpenAIVision:
        #     logger.info(f"正在加载OpenAI Vision模型: {model_name}")
        #     from src.openai_client import OpenAIVisionClient
        #     model = OpenAIVisionClient(
        #         model_name, api_key=access_key, user_name=user_name)
        # elif model_type == ModelType.ChatGLM:
        #     logger.info(f"正在加载ChatGLM模型: {model_name}")
        #     from src.chatglm import ChatGLMClient
        #     model = ChatGLMClient(model_name, user_name=user_name)
        # elif model_type == ModelType.LLaMA:
        #     logger.info(f"正在加载LLaMA模型: {model_name}")
        #     from src.llama import LLaMAClient
        #     model = LLaMAClient(model_name, user_name=user_name)
        elif model_type == ModelType.Unknown:
            logger.error(f"未知模型: {model_name}")
    except Exception as e:
        logger.error(e)
    # presudo_key = hide_middle_chars(access_key)
    if model is None:
        model = AzureOpenAIClient(
            api_key=conf.get("default_help_model.api_key", ""),
            user_name=user_name,
            azure_endpoint=conf.get("default_help_model.azure_endpoint", ""),
            model=conf.get("default_help_model.model_name", ""),
            deployment_name=conf.get("default_help_model.deployment_name", ""),
            api_version=conf.get("default_help_model.api_version", ""),
        )
        model_name = conf.get("default_help_model.model_name", "")
    msg = i18n("模型设置为了：") + f" {model_name}"
    logger.info(msg)
    return model


# if __name__ == "__main__":
#     with open("../config.json", "r") as f:
#         openai_api_key = json.load(f)["openai_api_key"]
#     print('key:', openai_api_key)
#     client = get_help_model(model_name="gpt-3.5-turbo",
#                        access_key=openai_api_key)[0]
#     chatbot = []
#     stream = False
#     # 测试账单功能
#     logger.info(colorama.Back.GREEN + "测试账单功能" + colorama.Back.RESET)
#     logger.info(client.billing_info())
#     # 测试问答
#     logger.info(colorama.Back.GREEN + "测试问答" + colorama.Back.RESET)
#     question = "巴黎是中国的首都吗？"
#     for i in client.predict(inputs=question, chatbot=chatbot, stream=stream):
#         logger.info(i)
#     logger.info(f"测试问答后history : {client.history}")
#     # 测试记忆力
#     logger.info(colorama.Back.GREEN + "测试记忆力" + colorama.Back.RESET)
#     question = "我刚刚问了你什么问题？"
#     for i in client.predict(inputs=question, chatbot=chatbot, stream=stream):
#         logger.info(i)
#     logger.info(f"测试记忆力后history : {client.history}")
#     # 测试重试功能
#     logger.info(colorama.Back.GREEN + "测试重试功能" + colorama.Back.RESET)
#     for i in client.retry(chatbot=chatbot, stream=stream):
#         logger.info(i)
#     logger.info(f"重试后history : {client.history}")
