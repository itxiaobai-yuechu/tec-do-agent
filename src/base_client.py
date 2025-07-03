from config import logger
import gradio as gr
import os
from src.presets import (
    MODEL_TOKEN_LIMIT,
    DEFAULT_TOKEN_LIMIT,
    TOKEN_OFFSET,
    REDUCE_TOKEN_FACTOR,
    STANDARD_ERROR_MSG,
    NO_APIKEY_MSG,
    BILLING_NOT_APPLICABLE_MSG,
    NO_INPUT_MSG,
    HISTORY_DIR,
    INITIAL_SYSTEM_PROMPT,
    PROMPT_TEMPLATE,
    WEBSEARCH_PTOMPT_TEMPLATE,
)
from src.utils import (
    i18n,
    construct_assistant,
    construct_user,
    save_chat_history_util,
    hide_middle_chars,
    count_token,
    new_auto_history_filename,
    get_history_names,
    init_history_list,
    get_history_list,
    replace_special_symbols,
    get_first_history_name,
    add_source_numbers,
    add_details,
    replace_today,
    chinese_preprocessing_func,
)


class BaseClient:
    def __init__(self, user_name):
        self.user_name = user_name
        self.history_file_path = get_first_history_name(user_name)
    # 在auto_name_chat_history内

    def save_chat_history(self, filename_without_json, chatbot):
        # chatbot ->原始chatbot,此时的filename without json
        # TODO 发生重复现象则使用number_filename来避免重复，历史对话标题通过文件中的内容来获取

        # 命名重复检测
        # full_path = os.path.join(
        #     HISTORY_DIR, self.user_name, f"{filename_without_json}.json")
        # repeat_file_index = 2
        # while os.path.exists(full_path):
        #     full_path = os.path.join(
        #         HISTORY_DIR, self.user_name, f"{repeat_file_index}_{filename_without_json}.json"
        #     )
        #     repeat_file_index += 1
        # filename = os.path.basename(full_path)
        # self.history_file_path = filename
        save_chat_history_util(chatbot, self.user_name,
                               f"{filename_without_json}.json", filename_without_json)
        # 对应historySelectList
        return init_history_list(self.user_name)

    def delete_chat_history(self, filename):
        if filename == "CANCELED":
            return gr.update(), gr.update(), gr.update()
        if filename == "":
            return i18n("你没有选择任何对话历史"), gr.update(), gr.update()
        if filename and not filename.endswith(".json"):
            filename += ".json"
        if filename == os.path.basename(filename):
            history_file_path = os.path.join(
                HISTORY_DIR, self.user_name, filename)
        else:
            history_file_path = filename
        md_history_file_path = history_file_path[:-5] + ".md"
        try:
            os.remove(history_file_path)
            os.remove(md_history_file_path)
            return i18n("删除对话历史成功"), get_history_list(self.user_name), []
        except:
            logger.info(f"删除对话历史失败 {history_file_path}")
            return (
                i18n("对话历史") + filename + i18n("已经被删除啦"),
                get_history_list(self.user_name),
                [],
            )
