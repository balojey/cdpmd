from typing import Literal

from fasthtml.common import *
from fhir.resources.task import Task

from cdpmd.ui.task_card import task_card


def task_bar(tasks: list[dict] | None):
    return Div(
        P(
            'Tasks',
            cls='is-size-3 has-text-weight-medium'
        ),
        Ul(
            *[
                Li(
                    task_card(task),
                    cls='my-3 is-size-4'
                ) for task in tasks
            ],
            cls='my-5',
            style='list-style-type: none;',
        ) if tasks != None and len(tasks) >= 1 else Div(
            'No pending task',
            cls='is-size-5 my-5',
        ),
        cls='cell is-col-span-4',
        id='task_bar'
    )