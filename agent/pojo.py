from enum import Enum
from typing import Optional, List, Tuple
from pydantic import BaseModel, Field
import operator
from typing import Annotated


class TaskStatusEnum(Enum):
    WAITING_START = "WAITING_START"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    WAITING = "WAITING"
    WAITING_INPUT = "WAITING_INPUT"
    WAITING_PLAN_JUDGE = "WAITING_PLAN_JUDGE"
    WAITING_REPLAN_JUDGE = "WAITING_REPLAN_JUDGE"


class GraphNodeEnum(Enum):
    JUDGE_PLAN = "judge_plan_node"
    USER_INPUT = "user_input_node"
    SINGLE_TASK = "single_task_node"
    JUDGE_REPLAN = "judge_replan_node"
    END = "end_node"

    def get_next_node(self):
        """获取下一个节点"""
        next_node_map = {
            GraphNodeEnum.JUDGE_PLAN: GraphNodeEnum.SINGLE_TASK.value,
            GraphNodeEnum.USER_INPUT: "single_task_node",
            GraphNodeEnum.SINGLE_TASK: GraphNodeEnum.SINGLE_TASK.value,
            GraphNodeEnum.END: None
        }
        return next_node_map.get(self)


class PlanExecuteState(BaseModel):
    objective: str = ""
    plan: List[str] = []
    task: str = ""
    # 其中为[(task,response),...]
    past_steps: Annotated[List[Tuple], operator.add] = []
    response: str = ""


class AppInterrupt(BaseModel):
    """app 中断"""
    interrupt_point: GraphNodeEnum = Field(
        description="中断点"
    )
    interrupt_value: str = Field(
        description="中断的提示"
    )
    state: Optional[PlanExecuteState] = None


class Plan(BaseModel):
    """未来计划"""
    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )


class ReplanResponse(BaseModel):
    """要执行的操作。"""
    action:  Plan = Field(
        description="要执行的操作"
    )


class Response(BaseModel):
    """响应"""
    response: str


class TaskStatus(BaseModel):
    plan_id: int
    status: TaskStatusEnum = TaskStatusEnum.RUNNING
    waiting_point: GraphNodeEnum
    waiting_input_ref: str = ""
    result: str = ""
    state: Optional[PlanExecuteState] = None
