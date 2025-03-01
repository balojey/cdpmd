from fasthtml.common import *


def header():
    return Div(
        Nav(
            Div(
                A('CDPMD', cls='navbar-item is-size-3 has-text-weight-bold', href='/'),
                Div(
                    A('About', cls='navbar-item', href='/login'),
                    A('Privacy Policy', cls='navbar-item', href='/login'),
                    A('Terms of Service', cls='navbar-item', href='/login'),
                    A('Contact', cls='navbar-item', href='/login'),
                    cls='navbar-end'
                ),
                cls='navbar-menu'
            ),
            cls='navbar',
        ),
        cls='hero is-primary',
    )
