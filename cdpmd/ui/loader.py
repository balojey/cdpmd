from fasthtml.common import *


def loader():
    return Div(
        Span(
            cls='loader',
            style='width: 20px; height: 20px; border: 2px solid #dbdbdb; border-radius: 50%; border-top-color: #485fc7; animation: spin 1s linear infinite; display: inline-block;'
        ),
        cls='htmx-indicator',
        style='opacity: 0; transition: opacity 200ms ease-in;'
    )