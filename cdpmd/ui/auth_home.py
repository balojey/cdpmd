from fasthtml.common import *
from fhir.resources.patient import Patient

from cdpmd.ui.header import header
from cdpmd.ui.patients_list import patients_list
from cdpmd.ui.patient_space import patient_space


def auth_home(patients: list[dict]):
    return Div(
        header(),
        Div(
            Div(
                patients_list(patients=patients),
                patient_space(),
                cls='grid is-gap-3',
                id="patient-details"
            ),
            cls='fixed-grid has-12-cols p-3 my-6 py-6'
        ),
        style='margin:0;padding:0;overflow:hidden;',
        cls='has-navbar-fixed-top'
    )