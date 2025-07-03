# -*- coding:utf-8 -*-

import locale
import os

import commentjson as json
import gradio as gr

pwd_path = os.path.abspath(os.path.dirname(__file__))

# 后面优化，使用翻译功能来实现


class I18nAuto:
    def __init__(self):
        language = os.environ.get("LANGUAGE", "auto")
        if language == "auto":
            # get the language code of the system (e.g. zh_CN)
            language = locale.getdefaultlocale()[0]
        self.language_map = {}
        file_path = os.path.join(pwd_path, f'../locale/{language}.json')
        self.file_is_exists = os.path.isfile(file_path)
        if self.file_is_exists:
            with open(file_path, "r", encoding="utf-8") as f:
                self.language_map.update(json.load(f))

    def __call__(self, key):
        if self.file_is_exists and key in self.language_map:
            return self.language_map[key]
        else:
            return key


i18n = I18nAuto()  # internationalization

# ChatGPT 设置
INITIAL_SYSTEM_PROMPT = "You are a helpful assistant."
API_HOST = "api.openai.com"
OPENAI_API_BASE = "https://api.openai.com/v1"
CHAT_COMPLETION_URL = "https://api.openai.com/v1/chat/completions"
IMAGES_COMPLETION_URL = "https://api.openai.com/v1/images/generations"
COMPLETION_URL = "https://api.openai.com/v1/completions"
BALANCE_API_URL = "https://api.openai.com/dashboard/billing/credit_grants"
USAGE_API_URL = "https://api.openai.com/dashboard/billing/usage"
HISTORY_DIR = os.path.join(pwd_path, '../history')
TEMPLATES_DIR = os.path.join(pwd_path, '../templates')

# assert文件
tecdo_path = os.path.dirname(pwd_path)
assets_path = os.path.join(pwd_path, "../assets")
favicon_path = os.path.join(pwd_path, "../assets/favicon.ico")

# 错误信息
STANDARD_ERROR_MSG = i18n("☹️发生了错误：")  # 错误信息的标准前缀
GENERAL_ERROR_MSG = i18n("获取对话时发生错误，请重试")
GENERATE_ERROR_MSG = i18n("生成时发生错误，请重试")
ERROR_RETRIEVE_MSG = i18n("请检查网络连接，或者API-Key是否有效。")
CONNECTION_TIMEOUT_MSG = i18n("连接超时，无法获取对话。")  # 连接超时
READ_TIMEOUT_MSG = i18n("读取超时，无法获取对话。")  # 读取超时
PROXY_ERROR_MSG = i18n("代理错误，无法获取对话。")  # 代理错误
SSL_ERROR_PROMPT = i18n("SSL错误，无法获取对话。")  # SSL 错误
NO_APIKEY_MSG = i18n("API key为空，请检查是否输入正确。")  # API key 长度不足 51 位
NO_INPUT_MSG = i18n("请输入对话内容。")  # 未输入对话内容
BILLING_NOT_APPLICABLE_MSG = i18n("账单信息不适用")  # 本地运行的模型返回的账单信息

TIMEOUT_STREAMING = 60  # 流式对话时的超时时间
TIMEOUT_ALL = 120  # 非流式对话时的超时时间
ENABLE_STREAMING_OPTION = True  # 是否启用选择选择是否实时显示回答的勾选框
HIDE_MY_KEY = True  # 如果你想在UI中隐藏你的 API 密钥，将此值设置为 True
CONCURRENT_COUNT = 100  # 允许同时使用的用户数量

SIM_K = 5
INDEX_QUERY_TEMPRATURE = 1.0

TITLE = i18n("Agent UI")
DESCRIPTION = i18n(
    "GitHub: [shibing624/chatgpt-webui](https://github.com/shibing624/chatgpt-webui)")

ONLINE_MODELS = [
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-1106",
    "gpt-4",
    "gpt-4-32k",
    "gpt-4-1106-preview",
    "gpt-4-turbo-preview",
    "gpt-4-vision-preview",
]

MODEL_TOKEN_LIMIT = {
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-16k": 16384,
    "gpt-3.5-turbo-1106": 16384,
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-1106-preview": 128000,
    "gpt-4-turbo-preview": 128000,
    "gpt-4-vision-preview": 128000,
}

LOCAL_MODELS = {
    "chatglm3-6b": "THUDM/chatglm3-6b",
    "llama-2-7b-chat": "TheBloke/Llama-2-7B-Chat-GPTQ",
    "yi-6b-chat-8bits": "01-ai/Yi-6B-Chat-8bits",
    "yi-6b-chat": "01-ai/Yi-6B-Chat",
}

MODELS = ONLINE_MODELS + list(LOCAL_MODELS.keys())
DEFAULT_MODEL = 0

os.makedirs(HISTORY_DIR, exist_ok=True)

TOKEN_OFFSET = 1000  # 模型的token上限减去这个值，得到软上限。到达软上限之后，自动尝试减少token占用。
DEFAULT_TOKEN_LIMIT = 3000  # 默认的token上限
REDUCE_TOKEN_FACTOR = 0.5  # 与模型token上限想乘，得到目标token数。减少token占用时，将token占用减少到目标token数以下。

REPLY_LANGUAGES = [
    "简体中文",
    "繁體中文",
    "English",
    "日本語",
    "Español",
    "Français",
    "Deutsch",
    "跟随问题语言（不稳定）"
]

HISTORY_NAME_METHODS = [
    i18n("根据日期时间"),
    i18n("第一条提问"),
    i18n("模型自动总结"),
]
WEBSEARCH_PTOMPT_TEMPLATE = """\
Web search results:

{web_results}
Current date: {current_date}

Instructions: Using the provided web search results, write a comprehensive reply to the given query. Make sure to cite results using [citation:x] notation after the reference, where x is a number. If the provided search results refer to multiple subjects with the same name, write separate answers for each subject.
Query: {query}
Reply in {reply_language}
"""

PROMPT_TEMPLATE = """\
Context information is below.
---------------------
{context_str}
---------------------
Current date: {current_date}.
Using the provided context information, write a comprehensive reply to the given query.
Make sure to cite results using [number] notation after the reference.
If the provided context information refer to multiple subjects with the same name, write separate answers for each subject.
Use prior knowledge only if the given context didn't provide enough information.
Answer the question: {query_str}
Reply in {reply_language}
"""

REFINE_TEMPLATE = """\
The original question is as follows: {query_str}
We have provided an existing answer: {existing_answer}
We have the opportunity to refine the existing answer
(only if needed) with some more context below.
------------
{context_msg}
------------
Given the new context, refine the original answer to better
Reply in {reply_language}
If the context isn't useful, return the original answer.
"""

SUMMARIZE_PROMPT = """Write a concise summary of the following:

{text}

CONCISE SUMMARY IN 中文:"""

SUMMARY_CHAT_SYSTEM_PROMPT = """\
Please summarize the following conversation for a chat topic.
No more than 16 characters.
No special characters.
Punctuation mark is banned.
Not including '.' ':' '?' '!' '“' '*' '<' '>'.
Reply in user's language.
"""

ALREADY_CONVERTED_MARK = "<!-- ALREADY CONVERTED BY PARSER. -->"
START_OF_OUTPUT_MARK = "<!-- SOO IN MESSAGE -->"
END_OF_OUTPUT_MARK = "<!-- EOO IN MESSAGE -->"

small_and_beautiful_theme = gr.themes.Soft(
    primary_hue=gr.themes.Color(
        c50="#EBFAF2",
        c100="#CFF3E1",
        c200="#A8EAC8",
        c300="#77DEA9",
        c400="#3FD086",
        c500="#02C160",
        c600="#06AE56",
        c700="#05974E",
        c800="#057F45",
        c900="#04673D",
        c950="#2E5541",
        name="small_and_beautiful",
    ),
    secondary_hue=gr.themes.Color(
        c50="#576b95",
        c100="#576b95",
        c200="#576b95",
        c300="#576b95",
        c400="#576b95",
        c500="#576b95",
        c600="#576b95",
        c700="#576b95",
        c800="#576b95",
        c900="#576b95",
        c950="#576b95",
    ),
    neutral_hue=gr.themes.Color(
        name="gray",
        c50="#f6f7f8",
        # c100="#f3f4f6",
        c100="#F2F2F2",
        c200="#e5e7eb",
        c300="#d1d5db",
        c400="#B2B2B2",
        c500="#808080",
        c600="#636363",
        c700="#515151",
        c800="#393939",
        # c900="#272727",
        c900="#2B2B2B",
        c950="#171717",
    ),
    radius_size=gr.themes.sizes.radius_sm,
).set(
    # button_primary_background_fill="*primary_500",
    button_primary_background_fill_dark="*primary_600",
    # button_primary_background_fill_hover="*primary_400",
    # button_primary_border_color="*primary_500",
    button_primary_border_color_dark="*primary_600",
    button_primary_text_color="wihte",
    button_primary_text_color_dark="white",
    button_secondary_background_fill="*neutral_100",
    button_secondary_background_fill_hover="*neutral_50",
    button_secondary_background_fill_dark="*neutral_900",
    button_secondary_text_color="*neutral_800",
    button_secondary_text_color_dark="white",
    # background_fill_primary="#F7F7F7",
    # background_fill_primary_dark="#1F1F1F",
    # block_title_text_color="*primary_500",
    block_title_background_fill_dark="*primary_900",
    block_label_background_fill_dark="*primary_900",
    input_background_fill="#F6F6F6",
    # chatbot_code_background_color="*neutral_950",
    chatbot_code_background_color_dark="*neutral_950",
)
