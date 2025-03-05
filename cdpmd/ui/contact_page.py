from fasthtml.common import *

from cdpmd.ui.header import header


content = '''
[**LinkenIn**](https://linkedin.com/in/ademola-balogun)\n
[**Twitter/X**](https://x.com/balojey)\n
[**GitHub**](https://github.com/balojey)\n

---
'''

def contact_page():
    return Div(
        header(),
        Div(
            Div(
                H1(
                    'Contact',
                    cls='title is-1'
                ),
                Div(content, cls='marked')
            ),
            cls='container my-6 py-6'
        )
    )