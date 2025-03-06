from fasthtml.common import *

from cdpmd.ui.card import card
from cdpmd.schemas import PredictorAgentResponseSchema


def cards(response: PredictorAgentResponseSchema, patient_id: str | None):
    return Div(
        *[
            card(card_details, patient_id) for card_details in response.cards
        ],
    )