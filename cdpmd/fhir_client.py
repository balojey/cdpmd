from pprint import pprint
import base64
import json
import httpx
from fhir.resources.patient import Patient
from fhir.resources.condition import Condition
from fhir.resources.medication import Medication
from fhir.resources.observation import Observation
from fhir.resources.communicationrequest import CommunicationRequest
from fhir.resources.coverageeligibilityrequest import CoverageEligibilityRequest
from fhir.resources.devicerequest import DeviceRequest
from fhir.resources.enrollmentrequest import EnrollmentRequest
from fhir.resources.medicationrequest import MedicationRequest
from fhir.resources.servicerequest import ServiceRequest
from fhir.resources.supplyrequest import SupplyRequest
from fhir.resources.task import Task

class FHIRClient:
    def __init__(self, base_url: str, auth=None, headers=None):
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            auth=auth,
            headers=headers or {},
            base_url=base_url,
            http2=True,  # Enable HTTP/2 for better performance
            timeout=httpx.Timeout(10.0)  # Set reasonable timeout
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.aclose()

    # Factory methods ----------------------------------------------------------
    @classmethod
    def for_no_auth(cls, base_url: str):
        return cls(base_url)

    @classmethod
    def for_bearer_token(cls, base_url: str, token: str):
        return cls(
            base_url,
            headers={"Authorization": f"Bearer {token}"}
        )

    @classmethod
    def for_basic_auth(cls, base_url: str, user: str, password: str):
        return cls(
            base_url,
            auth=(user, password)
        )

    @classmethod
    async def for_client_secret(cls, meldrx_base_url: str, workspace_id: str, 
                              client_id: str, client_secret: str, scope: str):
        token_url = f"{meldrx_base_url}/{workspace_id}/connect/token"
        fhir_url = f"{meldrx_base_url}/api/fhir/{workspace_id}"

        async with httpx.AsyncClient() as temp_client:
            response = await temp_client.post(
                token_url,
                data={
                    "grant_type": "client_credentials",
                    "scope": scope
                },
                headers={
                    "Authorization": f"Basic {base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode()}"
                }
            )
            response.raise_for_status()
            token_data = response.json()

        return cls.for_bearer_token(fhir_url, token_data["access_token"])

    # Core methods -------------------------------------------------------------
    async def read_resource(self, resource_type: str, resource_id: str | None = None):
        url = self._construct_url(resource_type, resource_id)
        response = await self.client.get(url)
        response.raise_for_status()
        
        data = response.json()
        resource_class = globals()[resource_type]
        
        if resource_id:
            return resource_class(**data)
        return [resource_class(**entry["resource"]) for entry in data.get("entry", [])]

    async def search_resource(self, resource_type: str, params: dict):
        url = self._construct_url(resource_type)
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def create_resource(self, resource_type: str, data: dict):
        url = self._construct_url(resource_type)
        response = await self.client.post(url, json=data)
        response.raise_for_status()
        return response.json()

    async def update_resource(self, resource_type: str, resource_id: str, data: dict):
        url = self._construct_url(resource_type, resource_id)
        response = await self.client.put(url, json=data)
        response.raise_for_status()
        return response.json()

    async def delete_resource(self, resource_type: str, resource_id: str):
        url = self._construct_url(resource_type, resource_id)
        response = await self.client.delete(url)
        response.raise_for_status()
        return response.json() if response.content else None

    # Helper methods -----------------------------------------------------------
    def _construct_url(self, resource_type: str, resource_id: str | None = None):
        path = f"/{resource_type}"
        if resource_id:
            path += f"/{resource_id}"
        return path