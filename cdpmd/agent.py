from pprint import pprint
import os
import functools
import json

from pydantic_ai import Agent, RunContext, Tool
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.openai import OpenAIModel

from cdpmd.schemas import ResourceType, PredictorAgentResponseSchema
from cdpmd.utils import AsyncCache


cache = AsyncCache(ttl=os.getenv('CACHE_TTL'))
model = OpenAIModel(
    'deepseek-chat',
    base_url=os.getenv('DEEPSEEK_BASE_URL'),
    api_key=os.getenv('DEEPSEEK_API_KEY')
)
cdpmd_agent = Agent(
    model,
    result_type=PredictorAgentResponseSchema,
    system_prompt=(
        "You are an advanced predictive decision support intervention model designed specifically for diabetes management and treatment. "
        "Your role is to assist healthcare providers by analyzing patient data, generating insights, and recommending evidence-based interventions. "
        "Ensure your responses are accurate, concise, and tailored to the clinical context. "
        "When making recommendations, prioritize guidelines from recognized medical authorities such as the ADA (American Diabetes Association). "
        "Always verify the availability and relevance of patient data before providing recommendations."
    )
)

@cache
async def predictor_query(
    patient: dict,
    conditions: dict,
    medications: dict,
    observations: dict,
    encounters: dict,
    diagnosticReports: dict,
    riskAssessments: dict,
    carePlans: dict,
) -> dict:
    result = await cdpmd_agent.run(
        f"""Act as an advanced predictive model for diabetes progression. Analyze the patient's 
        clinical data and produce an integrated risk and treatment recommendation report based 
        on ADA/EASD guidelines.

        Using the provided data below, perform the following tasks without using any formatting 
        or bullet points::
        - Patient Details = {patient}
        - Conditions = {conditions}
        - Observations = {observations}
        - medications = {medications}
        - encounters = {encounters}
        - diagnosticReports = {diagnosticReports}
        - riskAssessments = {riskAssessments}
        - carePlans = {carePlans}

        First, generate a concise clinical summary that highlights three to five key observations 
        regarding the patient's current glycemic control, trends in HbA1c and continuous glucose 
        monitoring (if available), and relevant comorbidities such as hypertension and dyslipidemia. 
        Next, perform risk stratification by estimating probabilities for both acute complications 
        (such as hypoglycemia and diabetic ketoacidosis) and chronic complications (such as retinopathy, 
        nephropathy, and neuropathy) and prioritize them accordingly. Then, propose an evidence-based 
        intervention plan that may include adjustments to medications, recommendations for changes in 
        monitoring frequency, and topics for patient education. Finally, identify any data gaps that, 
        if filled, could enhance the accuracy of predictions and decision support. Base your recommendations 
        on specific patient data points referenced from the supplied data, and integrate social determinants 
        of health where available to ensure a personalized analysis."""
    )
    return result.data.dict()
