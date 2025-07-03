import os
from src.utils import HISTORY_DIR
import json
from src.utils import new_auto_history_filename
from src.utils import get_history_names
import gradio as gr
from src.models import get_help_model
from config import conf, logger


def load_app(user_name):
    # if hasattr(request, "username") and request.username:
    #     logger.info(f"Get User Name: {request.username}")
    #     user_info, user_name = gr.Markdown.update(
    #         value=f"User: {request.username}"), request.username
    # else:
    #     user_info, user_name = gr.Markdown.update(
    #         value=f"", visible=False), ""

    # 通过request获取用户信息,聊天记录。。。
    # 通过配置获取模型信息
    model_name = conf.get("help_model.model_name", "")
    current_help_model = get_help_model(
        model_name=model_name, user_name=user_name)
    return current_help_model

# 参考以下


# outputs=[chatbot, status_display, historySelectList,
    #  single_turn_checkbox, temperature_slider],


def reset(user_name):
    """对聊天bot进行重置"""
    history_file_path = new_auto_history_filename(user_name)
    history_name = history_file_path[:-5]
    choices = get_history_names(user_name)
    if history_name not in choices:
        choices.insert(0, history_name)
    return [], gr.update(choices=choices, value=history_name),


def load_chat_history(history_select, user_name):
    # history_select中的值为选中的值
    history_file_path = os.path.join(
        HISTORY_DIR, user_name, f"{history_select}.json")
    with open(history_file_path, "r", encoding="utf-8") as f:
        history_data = json.load(f)

    return history_select, history_data["history"]
