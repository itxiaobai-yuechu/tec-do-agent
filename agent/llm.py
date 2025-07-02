from langchain_openai import AzureChatOpenAI
from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig
import vertexai
from config import logger
from openai import OpenAI
from config import config
from langchain.chat_models import init_chat_model
from langchain.prompts import SystemMessagePromptTemplate, ChatPromptTemplate


def create_azure_llm() -> AzureChatOpenAI:
    # 配置 Azure OpenAI 客户端
    return AzureChatOpenAI(
        api_key="0c7cf81130b7479f9391b327b2a1717f",  # API 密钥
        azure_endpoint="https://tecdoai-sweden-02.openai.azure.com",  # 替换为你的端点
        model="gpt-4o-mini",  # 选择模型
        deployment_name="tecdoai-sweden-02-gpt4o-mini",  # 替换为你的部署名称
        api_version="2024-08-01-preview",  # API 版本
    )


def chat_with_openai_in_azure(system_prompt: str, prompt: str) -> str:
    llm = create_azure_llm()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    response = llm.invoke(messages)
    return str(response.content)


def chat_once(llm, system_prompt: str, prompt: str) -> str:
    """
    单次对话
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    response = llm.invoke(messages)
    return str(response.content)


def chat_with_openai_in_azure_with_template(system_prompt_template: str, **kwargs) -> str:
    # 创建聊天提示模板
    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt_template),
    ])

    llm = create_azure_llm()
    chain = chat_prompt | llm
    response = chain.invoke(kwargs)
    return str(response.content)


def chat_with_gemini_in_vertexai(system_prompt: str, prompt: str) -> str:
    credentials = service_account.Credentials.from_service_account_file(
        filename=config.get('gemini_conf'))
    vertexai.init(project='ca-biz-vypngh-y97n', credentials=credentials)
    multimodal_model = GenerativeModel(
        model_name="gemini-2.5-flash-preview-04-17",
        system_instruction=system_prompt,
        generation_config=GenerationConfig(
            temperature=0.1)
    )

    # Query the model
    try:
        response = multimodal_model.generate_content(
            [
                prompt
            ]
        )
        return response.text
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        return ""


def translate_with_gemini_in_vertexai(context: str) -> str:
    system_prompt = "你是一个专业的中文翻译员，请只提供翻译后的中文内容，避免添加任何其他解释或信息。"
    prompt = f"请将以下内容翻译成中文：{context}"
    try:
        gemini_result = chat_with_gemini_in_vertexai(system_prompt, prompt)
        return gemini_result
    except Exception as e:
        return context


def generate_embedding_with_openai(text: str) -> list[float]:
    query_vectors = [
        vec.embedding
        for vec in OpenAI(api_key=config.get('openai_api_key'), base_url=config.get('openai_api_base')).embeddings.create(input=text, model=config.get('openai_embedding_model')).data]
    return query_vectors[0]
