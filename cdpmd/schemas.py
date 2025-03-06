from typing import Literal
from enum import Enum
from dataclasses import dataclass
from uuid import uuid4
import random

from pydantic import BaseModel, Field


def uuid_generator() -> str:
    return str(uuid4())

class ResourceType(Enum):
    patient = 'Patient'
    condition = 'Condition'
    medication = 'Medication'
    observation = 'Observation'
    encounter = 'Encounter'
    diagnostic_report = 'DiagnosticReport'
    risk_assessment = 'RiskAssessment'
    care_plan = 'CarePlan'
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

class ActionType(Enum):
    create = 'create'
    update = 'update'
    delete = 'delete'

class CardDetailsLinkType(Enum):
    absolute = 'absolute'
    smart = 'smart'

class Link(BaseModel):
    label: str
    url: str
    icon: str

class CardDetailsLink(BaseModel):
    label: str
    url: str
    type: Literal[
        CardDetailsLinkType.absolute.value,
        CardDetailsLinkType.smart.value
    ]

class PredictorAction(BaseModel):
    type: Literal[
        ActionType.create.value,
        ActionType.update.value,
        ActionType.delete.value,
    ]
    description: str
    resourceType: Literal[
        ResourceType.communication_request.value,
        ResourceType.coverage_eligibility_request.value,
        ResourceType.device_request.value,
        ResourceType.enrollment_request.value,
        ResourceType.medication_request.value,
        ResourceType.service_request.value,
        ResourceType.supply_request.value,
        ResourceType.task.value
    ]
    resourceId: str | None = Field(default_factory=uuid_generator)

class PredictorSuggestion(BaseModel):
    uuid: str = Field(default_factory=uuid_generator)
    label: str
    actions: list[PredictorAction]

class PredictorCardDetails(BaseModel):
    uuid: str = Field(default_factory=uuid_generator)
    summary: str
    detail: str
    indicator: Literal[
        Indicator.info.value,
        Indicator.warning.value,
        Indicator.critical.value,
    ]
    source: Link | None = None
    suggestions: list[PredictorSuggestion]
    links: list[CardDetailsLink] | None = None

class PredictorAgentResponseSchema(BaseModel):
    cards: list[PredictorCardDetails]


predictor_dummy_data = PredictorAgentResponseSchema(**{
    'cards': [
        {
            'summary': 'blah blah blah',
            'detail': 'blah blah blah blah blah blah blah blah blah blah',
            'indicator': 'info',
            'suggestions': [
                {
                    'label': 'blah',
                    'actions': [
                        {
                            'type': 'create',
                            'description': 'blah blah blah blah blah blah blah blah blah blah',
                            'resourceType': 'MedicationRequest',
                        },
                        {
                            'type': 'create',
                            'description': 'blah blah blah blah blah blah blah blah blah blah',
                            'resourceType': 'ServiceRequest'
                        },
                    ]
                }
            ],
            'source': {
                'label': 'CDPMD',
                'url': 'https://google.com',
                'icon': 'https://imgs.search.brave.com/MXd2gYPBb_8uzLekNa80ujdvyMZP8a33lPsO2Cw4m7c/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly90My5m/dGNkbi5uZXQvanBn/LzAxLzg1LzY2Lzk2/LzM2MF9GXzE4NTY2/OTY0MV9STDA1UG1Y/TTgyUXBwYVJCUVZz/dXk0SkRWcnpoenNh/SC5qcGc'
            }
        }
    ]
})