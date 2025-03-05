from fasthtml.common import *
from fhir.resources.patient import Patient

from cdpmd.ui.loader import loader


def patient_row(patient: dict):
    return Button(
        f"{patient['name'][0]['prefix'][0]} {patient['name'][0]['given'][0]} {patient['name'][0]['family']}",
        loader(),
        hx_get=f'/patients/{patient['id']}',
        hx_target='#patient-details-grid',
        hx_indicator='#loader',
        cls='button is-text is-medium is-fullwidth is-justify-content-left has-text-weight-normal',
        hx_disabled_elt='this',
        style='text-decoration: none;'
    )