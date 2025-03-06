from typing import Literal

from fasthtml.common import *

from cdpmd.ui.patient_first_space_content import patient_first_space_content
from cdpmd.ui.task_bar import task_bar
from cdpmd.schemas import PredictorAgentResponseSchema


def patient_space_content(
    response: PredictorAgentResponseSchema | None = None,
    patient: dict | None = None,
    tasks: list[dict] | None = None
):
    return Div(
        Div(
            patient_first_space_content(response=response, patient=patient),
            task_bar(tasks=tasks),
            cls='grid'
        ),
        cls='fixed-grid has-12-cols'
    )