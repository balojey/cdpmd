from fasthtml.common import *
from fhir.resources.task import Task


def task_card(task: Task):
    return Div(
        Div(
            Div(
                P(
                    task.description,
                ),
                cls='content'
            ),
            cls='card-content'
        ),
        Footer(
            A(
                'Delete',
                hx_get=f'/tasks/delete/{str(task.for_fhir.reference).split('/')[-1]}/{task.id}',
                cls='card-footer-item button is-danger',
                hx_target='#task_bar',
                hx_disabled_elt='this',
            ),
            cls='card-footer'
        ),
        cls='card',
    )