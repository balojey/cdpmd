from fasthtml.common import *

from cdpmd.ui.loader import loader
from cdpmd.ui.patient_row import patient_row


def patients_list(patients: list[dict]):
    return Div(
        P(
            'Patients',
            cls='is-size-3 has-text-weight-medium'
        ),
        Ul(
            *[
                Li(
                    patient_row(patient),
                    cls='my-3 is-size-4',
                ) for patient in patients
            ],
            cls='my-5'
        ),
        cls='cell is-col-span-3',
        style='overflow-y:auto;'
    )