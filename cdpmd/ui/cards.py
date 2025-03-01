from fasthtml.common import *

from cdpmd.ui.card import card
from cdpmd.schemas import CDPMDAgentResponseSchema


def cards(response: CDPMDAgentResponseSchema, patient_id: str | None):
    return Div(
        *[
            card(card_details, patient_id) for card_details in response.cards
        ],
    )