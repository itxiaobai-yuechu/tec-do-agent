from prompt import generate_sys_video_analysis_prompt
from fastmcp import Client
from pathlib import Path
import requests
import uuid
import os
import base64
from E_Commerce_Toolkit.Process_With_Retry import process_with_retry
from config import conf
import vertexai
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig
from google.oauth2 import service_account
from typing import Annotated
from langgraph.types import interrupt
from langchain_core.tools import tool
import asyncio
import json
from logger_config import logger
from pojo import AppInterrupt, GraphNodeEnum
import shutil
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@tool
async def user_input_tool(ref_content: str) -> str:
    """
    This function is used to get user input synchronously.

    Parameters:
    - ref_content(str): 参考内容，用于提示用户输入

    Returns:
    - user_input(str): 用户输入
    """

    # 发起中断
    human_message = interrupt(AppInterrupt(
        interrupt_point=GraphNodeEnum.USER_INPUT,
        interrupt_value=f"Please enter your input,ref:{ref_content} \n",
        state=None
    ))
    return human_message


@tool
async def search_by_product(product: str) -> list[str]:
    """
        This function is used to get the video url by product .

        Args:
            product(str): The name of the product or the type of the product.
    """
    video_url_list = []
    try:
        async with Client(conf.get('mcp_server_url')) as client:
            mcp_result = await client.call_tool("search_by_product_tool", {"product": product, "limit": 3})
            # 从result中提取video_url，处理不同类型的MCP结果
            for mcp_result_item in mcp_result:
                # 使用更安全的方式处理MCP结果
                try:
                    # 尝试将结果转换为字符串
                    result_str = str(mcp_result_item)
                    if result_str and result_str.strip():
                        video_url_list.append(result_str)
                except Exception as e:
                    logger.warning(f"无法处理MCP结果项: {e}")
                    continue
    except Exception as e:
        logger.error(f"MCP调用失败: {e}")
        # 返回一些示例视频URL作为fallback
        video_url_list = []
    return video_url_list


@tool
async def video_analysis(
    video_urls: Annotated[
        list[str],
        "视频链接列表,可以为本地视频链接，比如：/root/dzj/ad_agent/ad_agent_lg/temp/input/123/1.mp4，也可以为网络视频链接，比如：https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    ],
    analysis_dimensions: list[str]
) -> list[str]:
    """
        This function is used to analysis the video content.

        Args:
            video_urls(list[str]): 视频链接列表
            analysis_dimensions(list[str]): 分析维度列表
        Returns:
            list[str]: 分析结果列表
    """
    video_analysis_result_list = []
    # Initialize Vertex AI
    credentials = service_account.Credentials.from_service_account_file(
        filename=conf.get("gemini_conf"))
    vertexai.init(project='ca-biz-vypngh-y97n', credentials=credentials)

    # 为SYS_VIDEO_ANALYSIS_v3与PROMPT_v3重构提示词,重构response_schema

    # 重构SYS_VIDEO_ANALYSIS_v3
    SYS_VIDEO_ANALYSIS_PROMPT = generate_sys_video_analysis_prompt(
        analysis_dimensions)
    # 重构PROMPT_v3
    USER_VIDEO_ANALYSIS_PROMPT = f"以JSON格式输出视频的{','.join(analysis_dimensions)}"
    # 重构response_schema
    response_schema = {
        "type": "OBJECT",
        "properties": {}
    }
    for analysis_dimension in analysis_dimensions:
        response_schema["properties"][analysis_dimension] = {
            "type": "STRING",
            "description": f"{analysis_dimension}分析"
        }
    response_schema["required"] = analysis_dimensions

    for video_url in video_urls:
        if video_url.startswith("http"):
            video_data = requests.get(video_url).content
        else:
            with open(video_url, "rb") as file:
                video_data = file.read()

        # Load the model
        multimodal_model = GenerativeModel(
            model_name="gemini-2.5-flash-preview-04-17",
            system_instruction=SYS_VIDEO_ANALYSIS_PROMPT,
            generation_config=GenerationConfig(
                temperature=0.1, response_mime_type="application/json", response_schema=response_schema)
        )

        # Query the model
        try:
            response = multimodal_model.generate_content(
                [
                    USER_VIDEO_ANALYSIS_PROMPT,
                    Part.from_data(video_data, mime_type="video/mp4")
                ]
            )
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            continue
        # Extract and print the text response
        markdown_text = response.candidates[0].content.parts[0].text
        model_output_dict = markdown_text.replace('json', '')
        model_output_dict = model_output_dict.replace('`', '')
        markdown_text = model_output_dict.replace('\n', '')
        if not markdown_text.strip():
            logger.error(
                "Error: markdown_text is empty or contains only whitespace.")
            continue
        try:
            markdown_text = json.loads(markdown_text)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {e}")
            logger.error(f"Content of markdown_text: {markdown_text}")
            continue
        video_analysis_result_list.append(
            f"对于video_url:{video_url}, 分析结果如下{markdown_text}")
    return video_analysis_result_list


ECOMMERCE_GEMINI_API_KEY = conf.get('ecommerce_gemini_api_key')
ECOMMERCE_GPT_API_KEY = conf.get('ecommerce_gpt_api_key')


def get_unique_mp4_path_modern(output_dir: str) -> str:
    """
    使用pathlib获取output_dir下唯一的mp4文件的绝对路径

    Args:
        output_dir(str): 输出目录路径

    Returns:
        str: mp4文件的绝对路径
    """
    output_path = Path(output_dir)

    if not output_path.exists():
        raise FileNotFoundError(f"输出目录不存在: {output_dir}")

    # 查找所有mp4文件
    mp4_files = list(output_path.glob("*.mp4"))

    if not mp4_files:
        raise FileNotFoundError(f"在目录 {output_dir} 中没有找到mp4文件")

    if len(mp4_files) > 1:
        # 按修改时间排序，选择最新的
        mp4_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        logger.warning(f"在目录 {output_dir} 中找到多个mp4文件，选择最新的: {mp4_files[0]}")

    return str(mp4_files[0].resolve())


def cleanup_directories(dirs: list[str]) -> None:
    """
    删除input_dir和output_dir及其下的所有文件

    Args:
        input_dir (str): 输入目录路径
        output_dir (str): 输出目录路径
    """
    try:
        for dir in dirs:
            # 存在则删除
            if os.path.exists(dir):
                shutil.rmtree(dir)
                logger.info(f"已删除目录: {dir}")
    except Exception as e:
        logger.error(f"删除目录时发生错误: {e}")


def download_video_with_retry(video_url: str, video_path: str, max_retries: int = 3) -> bool:
    """
    下载视频文件，支持重试机制和错误处理

    Args:
        video_url (str): 视频URL
        video_path (str): 保存路径
        max_retries (int): 最大重试次数

    Returns:
        bool: 下载是否成功
    """
    # 配置重试策略
    retry_strategy = Retry(
        total=max_retries,
        status_forcelist=[429, 500, 502, 503, 504],
        backoff_factor=1
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    for attempt in range(max_retries):
        try:
            logger.info(f"正在下载视频 {video_url}，尝试 {attempt + 1}/{max_retries}")

            # 使用stream=True来避免内存问题
            response = session.get(video_url, stream=True, timeout=30)
            response.raise_for_status()

            # 获取文件大小
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            with open(video_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)

                        # 记录下载进度
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            if downloaded_size % (1024 * 1024) == 0:  # 每MB记录一次
                                logger.info(
                                    f"下载进度: {progress:.1f}% ({downloaded_size}/{total_size} bytes)")

            # 验证文件大小
            if total_size > 0:
                actual_size = os.path.getsize(video_path)
                if actual_size != total_size:
                    logger.warning(
                        f"文件大小不匹配: 期望 {total_size}, 实际 {actual_size}")
                    if attempt < max_retries - 1:
                        os.remove(video_path)
                        continue

            logger.info(f"视频下载成功: {video_path}")
            return True

        except requests.exceptions.ChunkedEncodingError as e:
            logger.error(f"下载中断 (尝试 {attempt + 1}/{max_retries}): {e}")
            if os.path.exists(video_path):
                os.remove(video_path)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
                continue
            else:
                logger.error(f"视频下载失败，已达到最大重试次数: {video_url}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求错误 (尝试 {attempt + 1}/{max_retries}): {e}")
            if os.path.exists(video_path):
                os.remove(video_path)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                logger.error(f"视频下载失败: {video_url}")
                return False

        except Exception as e:
            logger.error(f"未知错误 (尝试 {attempt + 1}/{max_retries}): {e}")
            if os.path.exists(video_path):
                os.remove(video_path)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                logger.error(f"视频下载失败: {video_url}")
                return False

    return False


@tool
def mixclip(
    video_urls: Annotated[
        list[str],
        """输入待混剪的视频素材链接列表，最多为3个
        请注意必须正确从对话内容中提取有效的视频链接（比如：https://www.youtube.com/watch?v=dQw4w9WgXcQ），否则会导致混剪失败""",
    ],
    product_name: Annotated[
        str, "产品名称，请确保产品名称有效，比如：Apple iPhone 15 Pro Max"
    ]
) -> str:
    """
    This function is used to mixclip videos.

    Args:
        video_urls (list[str]): List of video URLs.
        product_name (str): The name of the product.
    """
    _uuid = base64.urlsafe_b64encode(
        uuid.uuid4().bytes).decode('utf-8').rstrip('=')
    # 将url对应的视频下载到临时目录
    input_dir = conf.get('input_dir')+"/"+_uuid
    output_dir = conf.get('output_dir')+"/"+_uuid  # Initialize output_dir here
    try:
        os.makedirs(input_dir, exist_ok=True)
        # 使用改进的下载函数
        downloaded_videos = []
        for video_url in video_urls:
            video_name = video_url.split("/")[-1]
            video_path = os.path.join(input_dir, video_name)

            if download_video_with_retry(video_url, video_path):
                downloaded_videos.append(video_path)
            else:
                logger.error(f"无法下载视频: {video_url}")
                # 清理已创建的目录
                continue

        if len(downloaded_videos) == 0:
            cleanup_directories([input_dir])
            return "没有成功下载任何视频文件"

        os.makedirs(output_dir, exist_ok=True)
        output_time = 30
        num_output = 1
        keep_original_audio = False
        add_background_music = False
        background_music_path = None
        background_volume = 0.26
        result = process_with_retry(
            ECOMMERCE_GEMINI_API_KEY=ECOMMERCE_GEMINI_API_KEY,
            ECOMMERCE_GPT_API_KEY=ECOMMERCE_GPT_API_KEY,
            input_dir=input_dir,
            output_dir=output_dir,
            product_name=product_name,
            output_time=output_time,
            num_output=num_output,
            keep_original_audio=keep_original_audio,
            add_background_music=add_background_music,
            background_music_path=background_music_path,
            background_volume=background_volume
        )

        if result is not None and int(result) == 0:
            output_path = get_unique_mp4_path_modern(output_dir)
            # 混剪成功后清理临时目录
            return f"混剪结果保存在{output_path}"
        else:
            # 混剪失败后也清理临时目录
            return f"混剪失败，错误码：{result}"
    except Exception as e:
        logger.error(f"混剪失败: {e}")
        return f"混剪失败: {e}"
    finally:
        cleanup_directories([input_dir])


async def main():
    # Since search_by_product is now a sync function that handles async internally,
    # we can call it directly without await
    result = await search_by_product("可乐")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
    # video_urls = ['https://ins-obs.imcreator.vip/tiktok/video_v10033g50000cov651nog65u6vkbu4qg.mp4',
    #               'https://ins-obs.imcreator.vip/tiktok/video_v10033g50000cr8p7qnog65kqu04om90.mp4',
    #               'https://ins-obs.imcreator.vip/tiktok/video_v10033g50000cr8p7qnog65kqu04om90.mp4']
    # product_name = '奶粉'

    # print(mixclip(video_urls=video_urls, product_name=product_name))
