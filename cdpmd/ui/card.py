from fasthtml.common import *

from cdpmd.schemas import PredictorCardDetails, ActionType
from cdpmd.utils import get_payload
from cdpmd.ui.loader import loader


def card(card: PredictorCardDetails, patient_id: str | None):
    # print(card)
    indicator_colors = {
        'info': 'is-info',
        'warning': 'is-warning',
        'critical': 'is-danger'
    }
    button_colors = {
        ActionType.create.value: 'is-primary',
        ActionType.update.value: 'is-warning',
        ActionType.delete.value: 'is-danger',
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
                                *[
                                    Div(
                                        P(
                                            action.description,
                                        ),
                                        Button(
                                            f'{action.type.upper()} {action.resourceType}',
                                            loader(),
                                            cls=f'button {button_colors[action.type]} is-small mb-3',
                                            hx_vals=get_payload(
                                                description=action.description,
                                                action_type=action.type,
                                                resource_type=action.resourceType,
                                                resourceId=action.resourceId
                                            ),
                                            hx_post=f'/actions/{patient_id}',
                                            hx_target='#task_bar',
                                            hx_disabled_elt='this',
                                        ),
                                        cls='action',
                                    ) for action in suggestion.actions
                                ],
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