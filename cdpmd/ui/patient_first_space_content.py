from fasthtml.common import *
from fhir.resources.patient import Patient

from cdpmd.schemas import PredictorAgentResponseSchema
from cdpmd.ui.cards import cards
from cdpmd.ui.about_patient import about_patient


def patient_first_space_content(response: PredictorAgentResponseSchema | None = None, patient: dict | None = None):
    return Div(
        about_patient(patient=patient) if isinstance(patient, dict) else Div(),
        cards(response=response, patient_id=patient['id']) if isinstance(response, PredictorAgentResponseSchema) else Div(),
        cls='cell is-col-span-8'
    )
