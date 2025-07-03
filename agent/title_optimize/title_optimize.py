from langgraph.graph import StateGraph, START, END
from config import logger
from agent.utils import crawl_with_requests
from agent.lazada_selector import product_title_selector, product_description_selector
from pydantic import BaseModel


class TitleOptimizeState(BaseModel):
    url: str


async def crawl_product_info(state: TitleOptimizeState):
    url = state.url
    product_title = crawl_with_requests(url, product_title_selector)
    if (len(product_title) == 1):
        product_title = product_title[0]
    else:
        logger.error("title_optimize:title_selector_error")
    product_description = crawl_with_requests(
        url, product_description_selector)
    print(product_description)


graph = StateGraph(TitleOptimizeState)
graph.add_node("crawl_product_info", crawl_product_info)
graph.add_edge(START, "crawl_product_info")
graph.add_edge("crawl_product_info", END)

app = graph.compile()
