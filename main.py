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

import logfire
from fasthtml.common import *
from authlib.integrations.starlette_client import OAuth
from fhir.resources.patient import Patient
from fhir.resources.task import Task
from dotenv import load_dotenv
import asyncio

load_dotenv()

from cdpmd.fhir_client import FHIRClient
from cdpmd.schemas import ResourceType, CDPMD_Deps, CDPMDAgentResponseSchema, dummy_data
from cdpmd.ui.ordinary_home import ordinary_home
from cdpmd.ui.auth_home import auth_home
from cdpmd.ui.patient_space_content import patient_space_content
from cdpmd.ui.task_bar import task_bar
from cdpmd.utils import get_meldrx_client, get_reference_resources, get_tasks
from cdpmd.agent import query, new_query

logfire.configure(token=os.getenv('LOGFIRE_TOKEN'))
logfire.instrument_httpx(capture_all=True)

app, route = fast_app(
    hdrs=(
        Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/bulma@1.0.2/css/bulma.min.css'),
        Link(rel='preconnect', href='https://fonts.googleapis.com'),
        Link(rel='preconnect', href='https://fonts.gstatic.com', crossorigin=True),
        Link(rel='stylesheet', href='https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,500;1,700&display=swap'),
        Style('@keyframes spin { to { transform: rotate(360deg); } } .htmx-request .htmx-indicator {opacity: 1;}')
    ),
    pico=False
)
setup_toasts(app)

oauth = OAuth()
oauth.register(
    'meldrx',
    client_id=os.getenv('MELDRX_CLIENT_ID'),
    response_type='code',
    code_challenge_method='S256',
    server_metadata_url='https://app.meldrx.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile patient/*.*'}
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
    pprint(token)
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
        deps = json.dumps({
            'access_token': access_token,
            'meldrx_base_url': meldrx_base_url,
            'patient_id': patient_id
        })
        # result = await new_query(deps=deps)
        # print(result)
        meldrx_client: FHIRClient = get_meldrx_client(
            access_token=access_token,
            meldrx_base_url=meldrx_base_url
        )
        patient: Patient = await meldrx_client.read_resource(
            ResourceType.patient.value,
            patient_id
        )
        tasks: list[Task] | None = await get_tasks(
            patient_ref=f'{ResourceType.patient.value}/{patient_id}',
            access_token=access_token,
            meldrx_base_url=meldrx_base_url
        )
    except Exception as e:
        print(e)
        return add_toast(request.session, 'An error occured. Try reloading this page!', 'error')
    return patient_space_content(
        # response=result,
        response=CDPMDAgentResponseSchema(**dummy_data),
        patient=patient,
        tasks=tasks
    )

@app.route('/tasks/delete/{patient_id}/{task_id}')
async def delete_task(request: Request, patient_id: str, task_id: str):
    try:
        access_token = request.cookies['access_token']
        meldrx_base_url = request.cookies['meldrx_base_url']

        meldrx_client = get_meldrx_client(
            access_token=access_token,
            meldrx_base_url=meldrx_base_url
        )
        response = await meldrx_client.delete_resource(
            ResourceType.task.value,
            task_id
        )
        print(response)
        tasks: list[Task] | None = await get_tasks(
            patient_ref=f'{ResourceType.patient.value}/{patient_id}',
            access_token=access_token,
            meldrx_base_url=meldrx_base_url
        )
    except Exception as e:
        print(e)
        return add_toast(request.session, 'An error occured. Try reloading this page!', 'error')
    return task_bar(tasks)

@app.route('/tasks/create/{patient_id}')
async def create_task(request: Request, patient_id: str | None):
    try:
        access_token = request.cookies['access_token']
        meldrx_base_url = request.cookies['meldrx_base_url']

        meldrx_client = get_meldrx_client(
            access_token=access_token,
            meldrx_base_url=meldrx_base_url
        )

        body = await request.body()
        query_dict = urllib.parse.parse_qs(body.decode())
        query_dict = {k: v[0] for k, v in query_dict.items()}
        json_obj = {
            'id': str(uuid4()),
            'description': query_dict['description'],
            'intent': 'order',
            'status': 'accepted',
            'for': {
                'reference': f'Patient/{patient_id}'
            }
        }
        task = Task(**json_obj)
        result = await meldrx_client.create_resource(ResourceType.task.value, task.model_dump())
        tasks: list[Task] | None = await get_tasks(
            patient_ref=f'{ResourceType.patient.value}/{patient_id}',
            access_token=access_token,
            meldrx_base_url=meldrx_base_url
        )
    except Exception as e:
        print(e)
        return add_toast(request.session, 'An error occured. Try reloading this page!', 'error')
    return task_bar(tasks)

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