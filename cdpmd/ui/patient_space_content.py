from typing import Literal

from fasthtml.common import *
from fhir.resources.patient import Patient
from fhir.resources.task import Task

from cdpmd.ui.patient_first_space_content import patient_first_space_content
from cdpmd.ui.task_bar import task_bar
from cdpmd.schemas import CDPMDAgentResponseSchema, PredictorAgentResponseSchema


def patient_space_content(
    response: PredictorAgentResponseSchema | None = None,
    patient: Patient | None = None,
    tasks: list[Task] | None = None
):
    return Div(
        Div(
            patient_first_space_content(response=response, patient=patient),
            task_bar(tasks=tasks),
            cls='grid'
        ),
        cls='fixed-grid has-12-cols'
    )