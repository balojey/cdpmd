from fasthtml.common import *

from cdpmd.schemas import CardDetails
from cdpmd.utils import get_payload


def card(card: CardDetails, patient_id: str | None):
    print(card)
    indicator_colors = {
        'info': 'is-info',
        'warning': 'is-warning',
        'critical': 'is-danger'
    }
    return Div(
        Header(
            Div(
                Div(
                    card.indicator.upper(),
                    cls=f'tag {indicator_colors[card.indicator]}'
                ),
                cls='tags are-large ml-4 mt-4'
            ),
            P(
                card.summary,
                cls='card-header-title title is-4'
            ),
            cls='card-header is-flex-direction-column'
        ),
        Div(
            Div(
                P(
                    card.detail,
                    cls='mb-5'
                ),
                Div(
                    H5(
                        'Suggestions',
                        cls='title is-5'
                    ),
                    *[
                        Div(
                            Div(
                                H6(
                                    suggestion.label,
                                    cls='title is-6',
                                ),
                                P(
                                    suggestion.description,
                                ),
                                Button(
                                    'Create Task',
                                    cls='button is-primary is-small',
                                    hx_vals=get_payload(suggestion.description),
                                    hx_post=f'/tasks/create/{patient_id}',
                                    hx_target='#task_bar',
                                    hx_disabled_elt='this',
                                    _="""
                                    on htmx:afterOnLoad[successful] from body
                                        if detail.target == #task_bar
                                            remove closest .box
                                    """
                                ),
                                cls='action',
                            ),
                            cls='box'
                        ) for suggestion in card.suggestions if card.suggestions
                    ] or [Div('No Suggested Actions')]
                ),
                cls='content'
            ),
            cls='card-content'
        ),
        cls='card',
    )