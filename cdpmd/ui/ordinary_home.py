from fasthtml.common import *

from cdpmd.ui.header import header


def ordinary_home():
    return Div(
        header(),
        Div(
            Div(
                H1(
                    'Hello',
                    cls='title is-1'
                ),
                P(
                    'If you are seeing this page, it might be one of the following reasons:',
                    cls='is-size-3'
                ),
                Ol(
                    Li(
                        'Your Session has expired: If this is the case, go back to meldrx and relaunch the app.'
                    ),
                    Li('You don\'t know how to navigate this app. See ', A('here', href='https://youtube.com', target='_blank')),
                    cls='is-size-4 m-5'
                )
            ),
            cls='container my-6'
        )
    )