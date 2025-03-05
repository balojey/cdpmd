from fasthtml.common import *
from fhir.resources.task import Task

from cdpmd.utils import get_payload
from cdpmd.schemas import ActionType
from cdpmd.ui.loader import loader


def task_card(task: dict):
    return Div(
        Div(
            Div(
                Span(
                    task.get('focus', {'reference': 'Task/001'}).get('reference').split('/')[0],
                    cls='tag is-light mb-5 is-capitalized has-text-weight-normal'
                ),
                P(
                    task['description'],
                    cls='is-size-5 has-text-weight-bold'
                ),
                cls='content'
            ),
            cls='card-content'
        ),
        Footer(
            Button(
                'Delete',
                loader(),
                hx_post=f'/actions/{str(task["for"]["reference"]).split("/")[-1]}',
                hx_vals=get_payload(
                    action_type=ActionType.delete.value,
                    resourceId=task['id'],
                ),
                cls='card-footer-item button is-danger has-text-weight-normal',
                hx_target='#task_bar',
                hx_disabled_elt='this',
            ),
            cls='card-footer'
        ),
        cls='card',
    )
