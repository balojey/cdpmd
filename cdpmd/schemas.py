from typing import Literal
from enum import Enum
from dataclasses import dataclass

from pydantic import BaseModel, Field



class ResourceType(Enum):
    patient = 'Patient'
    condition = 'Condition'
    medication = 'Medication'
    observation = 'Observation'
    communication_request = 'CommunicationRequest'
    coverage_eligibility_request = 'CoverageEligibilityRequest'
    device_request = 'DeviceRequest'
    enrollment_request = 'EnrollmentRequest'
    medication_request = 'MedicationRequest'
    service_request = 'ServiceRequest'
    supply_request = 'SupplyRequest'
    task = 'Task'

class Indicator(Enum):
    info = 'info'
    warning = 'warning'
    critical = 'critical'

class SuggestionType(Enum):
    create = 'create'

class Suggestion(BaseModel):
    label: str
    description: str

class CardDetails(BaseModel):
    summary: str
    detail: str
    indicator: Literal[
        Indicator.info.value,
        Indicator.warning.value,
        Indicator.critical.value,
    ]
    suggestions: list[Suggestion]

class CDPMDAgentResponseSchema(BaseModel):
    cards: list[CardDetails]

class CDPMD_Deps(BaseModel):
    meldrx_base_url: str
    access_token: str
    patient_id: str
    cache: dict = Field(default_factory=dict)

dummy_data = {
    'cards': [
        {
            'summary': 'blah blah blah',
            'detail': 'blah blah blah blah blah blah blah blah blah blah',
            'indicator': 'info',
            'suggestions': [
                {
                    'label': 'blah',
                    'suggestion_type': 'create',
                    'description': 'blah blah blah blah blah blah blah blah blah blah',
                    'resource_type': 'Task'
                },
                {
                    'label': 'blah',
                    'suggestion_type': 'create',
                    'description': 'blah blah blah blah blah blah blah blah blah blah',
                    'resource_type': 'Task'
                },
                {
                    'label': 'blah',
                    'suggestion_type': 'create',
                    'description': 'blah blah blah blah blah blah blah blah blah blah',
                    'resource_type': 'Task'
                },
            ]
        },
        {
            'summary': 'blah blah blah',
            'detail': 'blah blah blah blah blah blah blah blah blah blah',
            'indicator': 'info',
            'suggestions': [
                {
                    'label': 'blah',
                    'suggestion_type': 'create',
                    'description': 'blah blah blah blah blah blah blah blah blah blah',
                    'resource_type': 'Task'
                },
                {
                    'label': 'blah',
                    'suggestion_type': 'create',
                    'description': 'blah blah blah blah blah blah blah blah blah blah',
                    'resource_type': 'Task'
                },
                {
                    'label': 'blah',
                    'suggestion_type': 'create',
                    'description': 'blah blah blah blah blah blah blah blah blah blah',
                    'resource_type': 'Task'
                },
            ]
        },
    ]
}