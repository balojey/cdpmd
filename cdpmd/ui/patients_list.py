from fasthtml.common import *
from fhir.resources.patient import Patient

from cdpmd.ui.loader import loader


def patients_list(patients: list[Patient]):
    return Div(
        P(
            'Patients',
            cls='is-size-3 has-text-weight-medium'
        ),
        Ul(
            *[
                Li(
                    A(
                        f"{patient.name[0].prefix[0]} {patient.name[0].given[0]} {patient.name[0].family}",
                        hx_get=f'/patients/{patient.id}',
                        hx_target='#patient-details-grid',
                        hx_push_url='true',
                        hx_indicator='.htmx-indicator',
                    ),
                    cls='my-3 is-size-4'
                ) for patient in patients
            ],
            cls='my-5'
        ),
        loader(),
        cls='cell is-col-span-3',
        style='overflow-y:auto;'
    )