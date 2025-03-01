from fasthtml.common import *


def patient_space():
    return Div(
        Div(
            Div(
                P(
                    'Nothing to show! Select a patient',
                    cls='is-size-3 has-text-weight-medium',
                    style='color:'
                ),
                cls='container is-flex is-justify-content-center is-align-content-center',
                style='height: 100vh;'
            ),
            id='patient-details-grid',
        ),
        cls='cell is-col-span-9'
    )