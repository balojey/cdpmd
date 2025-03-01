from fasthtml.common import *

from cdpmd.ui.header import header


content = '''
**Data Handling**  
- HIPAA & GDPR compliant architecture  
- Zero PHI storage policy (ephemeral data processing)  
- End-to-end AES-256 encryption  
- OAuth 2.0 protected FHIR access  

**Information Collected**  
- Temporary clinical data (max 24h retention)  
- De-identified usage metrics  
- Clinician credential tokens (JWT)  

**Third-Party Sharing**  
- No PHI sharing with external partners  
- Aggregated insights only for:  
  - Quality improvement  
  - Regulatory reporting  
  - Research collaborations  

**User Rights**  
- Full audit trail access  
- Data deletion requests (24h SLA)  
- Usage transparency reports  

**Security Measures**  
- SOC 2 Type II certified infrastructure  
- Annual penetration testing  
- Role-based access controls  
- Continuous vulnerability scanning  

**Contact**  
azeezbalogun74@gmail.com  

---
'''

def privacy_policy_page():
    return Div(
        header(),
        Div(
            Div(
                H1(
                    'Privacy Policy',
                    cls='title is-1'
                ),
                Div(content, cls='marked')
            ),
            cls='container my-6'
        )
    )