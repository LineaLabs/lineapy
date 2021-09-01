from typing import Optional, Dict, Any

from lineapy import Graph
from lineapy.data.types import LineaID
from lineapy.execution.executor import Executor


class Job:
    pass


class TriggerCondition:
    pass


class Scheduler:
    def __init__(self, executor: Executor):
        self._executor = executor

    def submit_job(self, program: Graph, inputs: Optional[Dict[LineaID, Any]] = None) -> Job:
        """
        TODO
        :param program:
        :param inputs:
        :return:
        """
        pass

    def set_trigger(self, artifact_id: LineaID, trigger: TriggerCondition) -> None:
        """

        :param artifact_id:
        :param trigger:
        :return:
        """
        pass

