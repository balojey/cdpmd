from fasthtml.common import *
from fhir.resources.patient import Patient

from cdpmd.utils import calculate_age


def about_patient(patient: Patient):
    return Div(
        Span(
            f'{patient['name'][0]['given'][0]} {patient['name'][0]['family']} ',
            cls='has-text-weight-bold is-size-2'
        ),
        Span(
            f'-- {str(patient['gender']).capitalize()} -- {calculate_age(str(patient['birthDate']))} years old',
            cls='is-size-4 has-text-weight-medium'
        ),
        cls='mb-5',
        style="border: 2px solid blue; padding: 20px; border-radius: 5px"
    )