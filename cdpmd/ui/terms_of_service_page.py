from fasthtml.common import *

from cdpmd.ui.header import header


content = '''
**Acceptable Use**  
1. Limited to licensed medical professionals  
2. Requires active FHIR server authorization  
3. Prohibits:  
   - Patient re-identification attempts  
   - Model reverse-engineering  
   - Commercial resale of outputs  

**Liability**  
- Decision support tool only - final clinical judgment required  
- No warranty for prediction accuracy  

**Intellectual Property**  
- User retains ownership of input data  
- System outputs licensed for care delivery use  

**Termination**  
- Immediate suspension for:  
  - Unauthorized data access  
  - Abuse detection  
  - Regulatory non-compliance  

**Modifications**  
- 30-day notice for material changes  
- Continued use constitutes acceptance  

---
'''

def terms_of_service_page():
    return Div(
        header(),
        Div(
            Div(
                H1(
                    'Terms of Service',
                    cls='title is-1'
                ),
                Div(content, cls='marked')
            ),
            cls='container my-6'
        )
    )