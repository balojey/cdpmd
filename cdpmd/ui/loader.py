from fasthtml.common import *


def loader():
    return Span(
        id='loader',
        cls='button is-loading is-small loader ml-5',
        style='background-color: inherit; border: none;'
    )