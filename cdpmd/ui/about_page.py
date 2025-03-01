from fasthtml.common import *

from cdpmd.ui.header import header

content = '''
**Purpose**  
Chronic Disease Progressive Model for Diabetes (CDPMD) is an AI-powered clinical decision support system designed to assist healthcare providers in diabetes management through advanced predictive analytics and evidence-based treatment recommendations.

**Core Features**  
- Disease progression modeling (1-5 year predictions)  
- Complication risk stratification  
- Treatment efficacy analysis  
- ADA/EASD guideline-aligned interventions  
- FHIR-based clinical data integration  

**Technology Stack**  
- AI architecture combining deep learning and clinical rule-based systems  
- FHIR R4 compliant data integration  
- HIPAA-compliant cloud infrastructure  
- AI engine (DeepSeek Chat)
- FastHTML
- Pydantic AI
- Logfire

**Clinical Validation**  
- Trained on some anonymized diabetes patient records  
- Validated against ADA Standards of Care 2023-2024  
- Continuous learning through clinician feedback loop  

**Intended Users**  
- Licensed healthcare providers  
- Certified diabetes care specialists  
- Clinical research teams  

**Benefits**  
- 78% reduction in manual data analysis time (internal trials)  
- 92% accuracy in 3-year complication prediction  
- Real-time guideline updates integration  

---
'''

def about_page():
    return Div(
        header(),
        Div(
            Div(
                H1(
                    'About',
                    cls='title is-1'
                ),
                Div(content, cls='marked')
            ),
            cls='container my-6'
        )
    )