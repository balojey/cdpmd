from fasthtml.common import *


def header():
    return Nav(
        Div(
            A('CDPMD', cls='navbar-item is-size-3 has-text-weight-bold', href='/'),
            Div(
                cls='navbar-start'
            ),
            Div(
                A('About', cls='navbar-item', href='/about'),
                A('Privacy Policy', cls='navbar-item', href='/privacy-policy'),
                A('Terms of Service', cls='navbar-item', href='/terms-of-service'),
                A('Contact', cls='navbar-item', href='/contact'),
                cls='navbar-end'
            ),
            cls='navbar-menu'
        ),
        cls='navbar is-fixed-top has-background-primary',
    )
