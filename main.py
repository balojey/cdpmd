from pprint import pprint
import logging
import sys
import json
import hashlib
import os
from typing import Literal
import urllib.parse
from datetime import datetime
from uuid import uuid4
from time import sleep

import logfire
from fasthtml.common import *
from authlib.integrations.starlette_client import OAuth
from fhir.resources.patient import Patient
from fhir.resources.task import Task
from dotenv import load_dotenv
import asyncio

load_dotenv()
print(os.getenv('MELDRX_CLIENT_ID'))

from cdpmd.fhir_client import FHIRClient
from cdpmd.schemas import (
    ResourceType, CDPMD_Deps, CDPMDAgentResponseSchema, dummy_data,
    predictor_dummy_data, PredictorAgentResponseSchema, ActionType
)
from cdpmd.ui.ordinary_home import ordinary_home
from cdpmd.ui.auth_home import auth_home
from cdpmd.ui.patient_space_content import patient_space_content
from cdpmd.ui.task_bar import task_bar
from cdpmd.ui.about_page import about_page
from cdpmd.ui.privacy_policy_page import privacy_policy_page
from cdpmd.ui.terms_of_service_page import terms_of_service_page
from cdpmd.ui.contact_page import contact_page
from cdpmd.utils import (
    get_meldrx_client, get_resources, get_reference_resources,
    get_tasks, add_source, generate_clinical_summary, create_cards,
    make_task, new_get_resource, delete_task
)
from cdpmd.agent import query, new_query, predictor_query

logfire.configure(token=os.getenv('LOGFIRE_TOKEN'))
logfire.instrument_httpx(capture_all=True)

app, route = fast_app(
    hdrs=(
        Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/bulma@1.0.2/css/bulma.min.css'),
        Link(rel='preconnect', href='https://fonts.googleapis.com'),
        Link(rel='preconnect', href='https://fonts.gstatic.com', crossorigin=True),
        Link(rel='stylesheet', href='https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,500;1,700&display=swap'),
        Style('.loader { display: none; } .htmx-request .loader { display: inline } .htmx-request.loader { display: inline }'),
        MarkdownJS(),
        # Script(src="https://kit.fontawesome.com/fc58daca91.js", crossorigin="anonymous"),
        Link(rel="icon", type="image/png", href="https://imgs.search.brave.com/MXd2gYPBb_8uzLekNa80ujdvyMZP8a33lPsO2Cw4m7c/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly90My5m/dGNkbi5uZXQvanBn/LzAxLzg1LzY2Lzk2/LzM2MF9GXzE4NTY2/OTY0MV9STDA1UG1Y/TTgyUXBwYVJCUVZz/dXk0SkRWcnpoenNh/SC5qcGc")
    ),
    pico=False
)
setup_toasts(app)

oauth = OAuth()
oauth.register(
    'meldrx',
    client_id=os.getenv('MELDRX_CLIENT_ID'),
    response_type=os.getenv('MELDRX_OIDC_RESPONSE_TYPE'),
    code_challenge_method=os.getenv('MELDRX_CODE_CHALLENGE_METHOD'),
    server_metadata_url=os.getenv('MELDRX_SERVER_METADATA'),
    client_kwargs={'scope': os.getenv('MELDRX_SCOPE'),}
)

@app.route('/launch')
async def launch(request: Request):
    callback_url = str(request.url_for('callback'))
    https_callback_url = callback_url.replace("http://", "https://")
    response = await oauth.meldrx.authorize_redirect(request, https_callback_url)
    meldrx_base_url = request.query_params['iss']
    response.set_cookie(
        'meldrx_base_url',
        meldrx_base_url,
        max_age=3600,
        httponly=True
    )
    return response

@app.route('/oidc-callback')
async def callback(request: Request):
    token = await oauth.meldrx.authorize_access_token(request)
    response = RedirectResponse(url='/')
    response.set_cookie(
        'access_token',
        token['access_token'],
        max_age=token['expires_in'],
        expires=token['expires_at'],
        httponly=True
    )
    return response

@app.route('/')
async def index(request: Request):
    if 'access_token' not in request.cookies:
        return ordinary_home()
    meldrx_client: FHIRClient = get_meldrx_client(
        access_token=request.cookies['access_token'],
        meldrx_base_url=request.cookies['meldrx_base_url'],
    )
    return auth_home(await meldrx_client.read_resource(ResourceType.patient.value))

@app.route('/patients/{patient_id}')
async def details(request: Request, patient_id: str):
    try:
        access_token = request.cookies['access_token']
        meldrx_base_url = request.cookies['meldrx_base_url']
        (
            patient,
            conditions,
            observations,
            medications,
            encounters,
            diagnostic_reports,
            risk_assessments,
            care_plans
        ) = await get_resources(access_token, meldrx_base_url, patient_id)
        response = await predictor_query(
            patient,
            conditions,
            observations,
            medications,
            encounters,
            diagnostic_reports,
            risk_assessments,
            care_plans
        )
        tasks = await new_get_resource(
            ResourceType.task.value,
            access_token,
            meldrx_base_url,
            patient_id
        )
    except Exception as e:
        print(e)
        return add_toast(request.session, 'An error occured. Try reloading this page!', 'error')
    return patient_space_content(
        response=PredictorAgentResponseSchema(**response),
        patient=patient,
        tasks=tasks
    )

@app.route('/actions/{patient_id}')
async def manage_tasks(request: Request, patient_id: str):
    try:
        access_token = request.cookies['access_token']
        meldrx_base_url = request.cookies['meldrx_base_url']

        body = await request.body()
        query_dict = urllib.parse.parse_qs(body.decode())
        query_dict = {k: v[0] for k, v in query_dict.items()}
        if query_dict['action_type'] == ActionType.create.value or query_dict['action_type'] == ActionType.update.value:
            await make_task(
                query_dict['description'],
                query_dict['resourceId'],
                query_dict['resource_type'],
                patient_id,
                access_token,
                meldrx_base_url
            )
        else:
            await delete_task(
                query_dict['resourceId'],
                access_token,
                meldrx_base_url,
            )
        tasks = await new_get_resource(
            ResourceType.task.value,
            access_token,
            meldrx_base_url,
            patient_id
        )
    except Exception as e:
        print(e)
        return add_toast(request.session, 'An error occured. Try reloading this page!', 'error', True)
    return task_bar(tasks)

@app.route('/cds-services')
async def cds_services(request: Request):
    return {
        "services": [
            {
                "hook": "patient-view",
                "title": "Chronic Disease Progressive Model For Diabetes (CDPMD)",
                "description": "A clinical decision support system for managing diabetes.",
                "id": "predictor",
                "prefetch": {
                    "patient": "Patient/{{context.patientId}}",
                    "conditions": "Condition?patient={{context.patientId}}",
                    "medications": "MedicationRequest?patient={{context.patientId}}",
                    "observations": "Observation?patient={{context.patientId}}",
                    "encounters": "Encounter?patient={{context.patientId}}",
                    "diagnosticReports": "DiagnosticReport?patient={{context.patientId}}",
                    "riskAssessments": "RiskAssessment?patient={{context.patientId}}",
                    "carePlans": "CarePlan?patient={{context.patientId}}",
                    # "goals": "Goal?patient={{context.patientId}}",
                    # "tasks": "Task?patient={{context.patientId}}",
                }
            }
        ]
    }


@app.route('/cds-services/predictor')
async def predictor(request: Request):
    body = await request.body()
    body = json.loads(body.decode())
    fhir_data = {}
    fhir_data['patient'] = body['prefetch']['patient']
    fhir_data['conditions'] = body['prefetch']['conditions']
    fhir_data['medications'] = body['prefetch']['medications']
    fhir_data['observations'] = body['prefetch']['observations']
    fhir_data['encounters'] = body['prefetch']['encounters']
    fhir_data['diagnosticReports'] = body['prefetch']['diagnosticReports']
    fhir_data['riskAssessments'] = body['prefetch']['riskAssessments']
    fhir_data['carePlans'] = body['prefetch']['carePlans']
    summary = await generate_clinical_summary(fhir_data)
    # print(summary)
    return await create_cards(summary, str(request.base_url))
    

@app.route('/about')
async def about():
    return about_page()

@app.route('/privacy-policy')
async def privacy_policy():
    return privacy_policy_page()

@app.route('/terms-of-service')
async def terms_of_service():
    return terms_of_service_page()

@app.route('/contact')
async def contact():
    return contact_page()

serve()