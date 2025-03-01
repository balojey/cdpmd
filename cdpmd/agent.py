import os
import functools
import json

from pydantic_ai import Agent, RunContext, Tool
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.openai import OpenAIModel

from cdpmd.schemas import CDPMD_Deps, CDPMDAgentResponseSchema, ResourceType
from cdpmd.utils import get_resource, new_get_resource, AsyncCache


cache = AsyncCache(ttl=os.getenv('CACHE_TTL'))
# model = GeminiModel('gemini-1.5-flash')
model = OpenAIModel(
    'deepseek-chat',
    base_url=os.getenv('DEEPSEEK_BASE_URL'),
    api_key=os.getenv('DEEPSEEK_API_KEY')
)
cdpmd_agent = Agent(
    model,
    deps_type=CDPMD_Deps,
    result_type=CDPMDAgentResponseSchema,
    # tools=[
    #     Tool(get_resource, takes_ctx=True)
    # ],
    system_prompt=(
        "You are an advanced predictive decision support intervention model designed specifically for diabetes management and treatment. "
        "Your role is to assist healthcare providers by analyzing patient data, generating insights, and recommending evidence-based interventions. "
        # "Use the `get_resource` function to retrieve necessary FHIR resources such as Patient, Condition, Medication, and Observation data. "
        "Ensure your responses are accurate, concise, and tailored to the clinical context. "
        "When making recommendations, prioritize guidelines from recognized medical authorities such as the ADA (American Diabetes Association). "
        "Always verify the availability and relevance of patient data before providing recommendations."
    )
)

@cache
async def new_query(deps: str) -> CDPMDAgentResponseSchema:
    deps = CDPMD_Deps(**json.loads(deps))
    result = await cdpmd_agent.run(
        f"""Act as an advanced predictive model for diabetes progression. Analyze the patient's clinical data to:
    1. Predict likely disease progression over the next 1-5 years
    2. Identify key risk factors for acute complications (e.g., hypoglycemia, DKA) 
    and chronic complications (retinopathy, nephropathy, neuropathy)
    3. Assess current treatment efficacy
    4. Recommend evidence-based interventions

    Here are the patient's clinical data:
    - Patient Details = {await new_get_resource(ResourceType.patient.value, deps.access_token, deps.meldrx_base_url, deps.patient_id)}
    - Conditions = {await new_get_resource(ResourceType.condition.value, deps.access_token, deps.meldrx_base_url, deps.patient_id)}
    - Medications = {await new_get_resource(ResourceType.medication.value, deps.access_token, deps.meldrx_base_url, deps.patient_id)}
    - Observations = {await new_get_resource(ResourceType.observation.value, deps.access_token, deps.meldrx_base_url, deps.patient_id)}
    - Tasks = {await new_get_resource(ResourceType.task.value, deps.access_token, deps.meldrx_base_url, deps.patient_id)}

    Required analysis:
    - Evaluate glycemic control using HbA1c trends and CGM data (if available)
    - Analyze medication adherence patterns
    - Consider comorbidities (hypertension, dyslipidemia)
    - Incorporate social determinants of health from available data

    Format response with:
    [1] Clinical Summary (3-5 key observations)
    [2] Risk Stratification (prioritized complications with probability estimates)
    [3] Intervention Plan (medication adjustments, monitoring frequency, patient education topics)
    [4] Data Gaps (missing information needed for improved predictions)

    Base recommendations on ADA/EASD guidelines and reference specific patient data 
    points used in your analysis.""",
        deps=deps
    )
    return result.data

@functools.cache
async def query(deps: str) -> CDPMDAgentResponseSchema:
    deps = CDPMD_Deps(**json.loads(deps))
    result = await cdpmd_agent.run(
        """Act as an advanced predictive model for diabetes progression. Analyze the patient's clinical data to:
    1. Predict likely disease progression over the next 1-5 years
    2. Identify key risk factors for acute complications (e.g., hypoglycemia, DKA) 
    and chronic complications (retinopathy, nephropathy, neuropathy)
    3. Assess current treatment efficacy
    4. Recommend evidence-based interventions

    Required analysis:
    - Evaluate glycemic control using HbA1c trends and CGM data (if available)
    - Analyze medication adherence patterns
    - Consider comorbidities (hypertension, dyslipidemia)
    - Incorporate social determinants of health from available data

    Format response with:
    [1] Clinical Summary (3-5 key observations)
    [2] Risk Stratification (prioritized complications with probability estimates)
    [3] Intervention Plan (medication adjustments, monitoring frequency, patient education topics)
    [4] Data Gaps (missing information needed for improved predictions)

    Base recommendations on ADA/EASD guidelines and reference specific patient data 
    points used in your analysis.""",
        deps=deps
    )
    return result.data