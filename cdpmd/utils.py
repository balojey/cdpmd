from pprint import pprint
from typing import Literal, Union, List, Dict, Callable, Any, Tuple, Optional
import json
from functools import wraps
import hashlib
from datetime import datetime
import time
import os
import httpx

from httpx import AsyncClient
from pydantic_ai import RunContext
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

from cdpmd.schemas import CDPMD_Deps, ResourceType, CDPMDAgentResponseSchema, Link, CardDetailsLink, CardDetailsLinkType
from cdpmd.fhir_client import FHIRClient


class AsyncCache:
    def __init__(self, ttl: Optional[float] = 300, cache_file: str = "cache.json"):
        """
        Args:
            ttl: Time-to-live in seconds for cache entries. 
                 None means no expiration. Default: 300s (5 minutes)
            cache_file: Path to the JSON file for storing the cache.
        """
        self.cache_file = cache_file
        self.ttl = float(ttl) if ttl is not None else None
        self.cache: Dict[str, Tuple[float, Any]] = self._load_cache()

    def _load_cache(self) -> Dict[str, Tuple[float, Any]]:
        """Load cache from the JSON file."""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    # Handle corrupted or empty JSON file
                    return {}
        return {}

    def _save_cache(self):
        """Save cache to the JSON file."""
        with open(self.cache_file, "w") as file:
            json.dump(self.cache, file, default=str)

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            key = self._make_key(args, kwargs)

            # Check cache and validate TTL
            if key in self.cache:
                expiration, cached_value = self.cache[key]

                if self.ttl is None or time.time() < expiration:
                    return cached_value

                # Remove expired entry
                del self.cache[key]
                self._save_cache()

            # Execute and cache result
            result = await func(*args, **kwargs)
            expiration = time.time() + self.ttl if self.ttl else None
            self.cache[key] = (expiration, result)
            self._save_cache()
            return result

        return wrapper

    def _make_key(self, args: Tuple, kwargs: Dict) -> str:
        """Create unique hash key from arguments."""
        patient_id = args[0]['id']
        # dumped = json.dumps({
        #     'args': args,
        #     'kwargs': {
        #         k: v for k, v in kwargs.items()
        #         if k not in ['ttl']  # Exclude TTL from key generation
        #     }
        # }, sort_keys=True, default=str)
        # return hashlib.sha256(dumped.encode()).hexdigest()
        return patient_id

    def clear(self):
        """Clear all cached entries and save the empty cache to the file."""
        self.cache.clear()
        self._save_cache()

    def set_ttl(self, ttl: Optional[float]):
        """Update TTL for new entries (does not affect existing entries)."""
        self.ttl = ttl

    def cleanup_expired(self):
        """Remove all expired entries from the cache and save the updated cache."""
        current_time = time.time()
        expired_keys = [
            key for key, (expiration, _) in self.cache.items()
            if self.ttl is not None and expiration < current_time
        ]
        for key in expired_keys:
            del self.cache[key]
        if expired_keys:
            self._save_cache()

class AsyncFhirCache:
    def __init__(self, ttl: Optional[float] = 300, cache_file: str = "cache.json"):
        """
        Args:
            ttl: Time-to-live in seconds for cache entries. 
                 None means no expiration. Default: 300s (5 minutes)
            cache_file: Path to the JSON file for storing the cache.
        """
        self.cache_file = cache_file
        self.ttl = float(ttl) if ttl is not None else None
        self.cache: Dict[str, Tuple[float, Any]] = self._load_cache()

    def _load_cache(self) -> Dict[str, Tuple[float, Any]]:
        """Load cache from the JSON file."""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    # Handle corrupted or empty JSON file
                    return {}
        return {}

    def _save_cache(self):
        """Save cache to the JSON file."""
        with open(self.cache_file, "w") as file:
            json.dump(self.cache, file, default=str)

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            key = self._make_key(args, kwargs)

            # Check cache and validate TTL
            if key in self.cache:
                expiration, cached_value = self.cache[key]

                if self.ttl is None or time.time() < expiration:
                    return cached_value

                # Remove expired entry
                del self.cache[key]
                self._save_cache()

            # Execute and cache result
            result = await func(*args, **kwargs)
            expiration = time.time() + self.ttl if self.ttl else None
            self.cache[key] = (expiration, result)
            self._save_cache()
            return result

        return wrapper

    def _make_key(self, args: Tuple, kwargs: Dict) -> str:
        """Create unique hash key from arguments."""
        patient_id = args[-1]
        # dumped = json.dumps({
        #     'args': args,
        #     'kwargs': {
        #         k: v for k, v in kwargs.items()
        #         if k not in ['ttl']  # Exclude TTL from key generation
        #     }
        # }, sort_keys=True, default=str)
        # return hashlib.sha256(dumped.encode()).hexdigest()
        return patient_id

    def clear(self):
        """Clear all cached entries and save the empty cache to the file."""
        self.cache.clear()
        self._save_cache()

    def set_ttl(self, ttl: Optional[float]):
        """Update TTL for new entries (does not affect existing entries)."""
        self.ttl = ttl

    def cleanup_expired(self):
        """Remove all expired entries from the cache and save the updated cache."""
        current_time = time.time()
        expired_keys = [
            key for key, (expiration, _) in self.cache.items()
            if self.ttl is not None and expiration < current_time
        ]
        for key in expired_keys:
            del self.cache[key]
        if expired_keys:
            self._save_cache()

fhir_cache = AsyncFhirCache(os.getenv('CACHE_TTL'), 'fhir_cache.json')

FHIRResource = Union[
    Condition, Medication, Observation, CommunicationRequest,
    CoverageEligibilityRequest, DeviceRequest, EnrollmentRequest,
    MedicationRequest, ServiceRequest, SupplyRequest, Task
]

async def get_reference_resources(
    resources: List[Union[FHIRResource, None]],
    patient_ref: str
) -> List[FHIRResource]:
    """Filters FHIR resources to those associated with the specified patient.
    
    Args:
        resources: List of FHIR resources to filter
        patient_ref: Full patient reference string (e.g. 'Patient/123')
        
    Returns:
        List of resources belonging to the specified patient
    """
    filtered = []
    for resource in resources:
        if not resource:
            continue
            
        # Handle Task resource special case
        if isinstance(resource, Task):
            if resource.for_fhir and resource.for_fhir.reference == patient_ref:
                filtered.append(resource)
            continue
            
        # Standard patient reference check
        if resource.subject and resource.subject.reference == patient_ref:
            filtered.append(resource)
            
    return filtered

async def new_get_resource(
    resource_type: Literal[
        ResourceType.patient.value,
        ResourceType.condition.value,
        ResourceType.medication.value,
        ResourceType.observation.value,
        ResourceType.encounter.value,
        ResourceType.diagnostic_report.value,
        ResourceType.risk_assessment.value,
        ResourceType.care_plan.value,
        ResourceType.task.value,
    ],
    access_token: str,
    meldrx_base_url: str,
    patient_id: str
) -> Union[FHIRResource, List[FHIRResource], None]:
    """Retrieves FHIR resources from the server with patient context awareness."""
    
    async with get_meldrx_client(access_token, meldrx_base_url) as client:
        resource_id = patient_id if resource_type == ResourceType.patient.value else None
        
        try:
            resource = await client.read_resource(
                resource_type=resource_type,
                resource_id=resource_id,
                params={
                    'patient': patient_id
                } if resource_type != ResourceType.patient.value else None
            )
            # print(resource, '\n\n\n')
            
            return resource
            
        except httpx.HTTPStatusError as e:
            print(f"FHIR API error for {resource_type}: {e}")
            return None

@fhir_cache
async def get_resources(
    access_token: str,
    meldrx_base_url: str,
    patient_id: str
) -> list:
    patient = await new_get_resource(
        ResourceType.patient.value,
        access_token,
        meldrx_base_url,
        patient_id
    )
    conditions = await new_get_resource(
        ResourceType.condition.value,
        access_token,
        meldrx_base_url,
        patient_id
    )
    observations = await new_get_resource(
        ResourceType.observation.value,
        access_token,
        meldrx_base_url,
        patient_id
    )
    medications = await new_get_resource(
        ResourceType.medication_request.value,
        access_token,
        meldrx_base_url,
        patient_id
    )
    encounters = await new_get_resource(
        ResourceType.encounter.value,
        access_token,
        meldrx_base_url,
        patient_id
    )
    diagnostic_reports = await new_get_resource(
        ResourceType.diagnostic_report.value,
        access_token,
        meldrx_base_url,
        patient_id
    )
    risk_assessments = await new_get_resource(
        ResourceType.risk_assessment.value,
        access_token,
        meldrx_base_url,
        patient_id
    )
    care_plans = await new_get_resource(
        ResourceType.care_plan.value,
        access_token,
        meldrx_base_url,
        patient_id
    )
    return [patient, conditions, observations, medications, encounters, diagnostic_reports, risk_assessments, care_plans]

async def get_resource(
    ctx: RunContext[CDPMD_Deps],
    resource_type: Literal[
        ResourceType.patient.value,
        ResourceType.condition.value,
        ResourceType.medication.value,
        ResourceType.observation.value,
        ResourceType.task.value,
    ]
) -> Union[FHIRResource, List[FHIRResource], None]:
    """Retrieves FHIR resources from the server with patient context awareness.
    
    Args:
        resource_type: Type of FHIR resource to retrieve
        
    Returns:
        Single resource or list of resources filtered to the current patient
        
    Examples:
        >>> # Get patient record
        >>> patient = await get_resource('Patient')
        >>>
        >>> # Get all observations for patient
        >>> observations = await get_resource('Observation')
    """
    cache_key = f"{resource_type}_{ctx.deps.patient_id}"
    
    # Return cached result if available
    if cache_key in ctx.deps.cache:
        return ctx.deps.cache[cache_key]
    
    async with get_meldrx_client(ctx.deps.access_token, ctx.deps.meldrx_base_url) as client:
        resource_id = ctx.deps.patient_id if resource_type == ResourceType.patient.value else None
        
        try:
            resource = await client.read_resource(
                resource_type=resource_type,
                resource_id=resource_id
            )
            
            # Filter and process resources
            if isinstance(resource, list):
                patient_ref = f"Patient/{ctx.deps.patient_id}"
                resource = await get_reference_resources(resource, patient_ref)
            
            # Store in cache before returning
            ctx.deps.cache[cache_key] = resource
            return resource
            
        except httpx.HTTPStatusError as e:
            ctx.logger.error(f"FHIR API error for {resource_type}: {e}")
            return None

def get_meldrx_client(access_token: str, meldrx_base_url: str) -> FHIRClient:
    """Factory for authenticated FHIR client with connection pooling."""
    return FHIRClient.for_bearer_token(
        base_url=meldrx_base_url,
        token=access_token
    )

async def get_tasks(
    patient_ref: str,
    access_token: str,
    meldrx_base_url: str
) -> Union[List[Task], None]:
    """Retrieves tasks associated with a specific patient."""
    async with get_meldrx_client(access_token, meldrx_base_url) as client:
        try:
            tasks = await client.read_resource(ResourceType.task.value)
            return await get_reference_resources(tasks, patient_ref)
        except httpx.HTTPStatusError as e:
            return None

def get_payload(**kwargs) -> str:
    """Creates a standardized JSON payload for API requests."""
    payload = {}
    for k, v in kwargs.items():
        payload[k] = v
    return json.dumps(payload)

async def make_task(
    description: str,
    resource_id: str,
    resource_type: Literal[
        ResourceType.communication_request.value,
        ResourceType.coverage_eligibility_request.value,
        ResourceType.device_request.value,
        ResourceType.enrollment_request.value,
        ResourceType.medication_request.value,
        ResourceType.service_request.value,
        ResourceType.supply_request.value,
        ResourceType.task.value
    ],
    patient_id: str,
    access_token: str,
    meldrx_base_url: str
) -> None:
    json_obj = {
        'description': description,
        'intent': 'order',
        'status': 'accepted',
        'for': {
            'reference': f'Patient/{patient_id}'
        },
        'resourceType': 'Task',
        'focus': {
            'reference': f'{resource_type}/{resource_id}'
        }
    }
    async with get_meldrx_client(access_token, meldrx_base_url) as client:
        try:
            response = await client.create_resource(
                resource_type=ResourceType.task.value,
                data=json_obj
            )
        except httpx.HTTPStatusError as e:
            print(f"FHIR API error for {ResourceType.task.value}: {e}")
            return None

async def delete_task(resource_id: str, access_token: str, meldrx_base_url: str) -> None:
    async with get_meldrx_client(access_token, meldrx_base_url) as client:
        try:
            response = await client.delete_resource(
                ResourceType.task.value,
                resource_id
            )
        except httpx.HTTPStatusError as e:
            print(f"FHIR API error for {ResourceType.task.value}: {e}")
            return None

async def add_source(
    response_dict: dict,
    url: str,
    label: str = 'Chronic Disease Progressive Model for Diabetes (CDPMD)',
    icon: str = 'https://imgs.search.brave.com/MXd2gYPBb_8uzLekNa80ujdvyMZP8a33lPsO2Cw4m7c/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly90My5m/dGNkbi5uZXQvanBn/LzAxLzg1LzY2Lzk2/LzM2MF9GXzE4NTY2/OTY0MV9STDA1UG1Y/TTgyUXBwYVJCUVZz/dXk0SkRWcnpoenNh/SC5qcGc'
):
    for card in response_dict['cards']:
        card['source'] = Link(label=label, icon=icon, url=url).dict()
    return response_dict

def calculate_age(date_of_birth: str) -> int:
    """Calculates age based on date of birth.
    
    Args:
        date_of_birth: Date of birth in 'YYYY-MM-DD' format.
        
    Returns:
        Age in years.
    """
    birth_date = datetime.strptime(date_of_birth, '%Y-%m-%d')
    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age


async def generate_clinical_summary(fhir_data: dict) -> str:
    """
    Generate a clinical summary from a set of FHIR resources.
    
    Args:
        fhir_data (dict): Dictionary with keys such as "patient", "conditions",
            "medications", "observations", "encounters", "diagnosticReports",
            "riskAssessments", "carePlans", "goals", and "tasks".
    
    Returns:
        str: A clinical summary string.
    """
    summary_parts = []
    
    # Patient demographics
    patient = fhir_data.get("patient", {})
    gender = patient.get("gender", "unknown")
    birth_date = patient.get("birthDate", "unknown")
    age = "unknown"
    if birth_date != "unknown":
        try:
            birth_year = int(birth_date.split("-")[0])
            current_year = datetime.now().year
            age = current_year - birth_year
        except Exception:
            pass
    summary_parts.append(f"The patient is a {age}-year-old {gender}.")
    
    # Conditions: list all condition names (using text from code element)
    conditions = fhir_data.get("conditions", {}).get('entry', [])
    condition_names = []
    for cond in conditions:
        code = cond.get("code", {})
        # Try to get a human-readable text description
        condition_text = code.get("text")
        if condition_text:
            condition_names.append(condition_text)
    if condition_names:
        summary_parts.append("History of " + ", ".join(condition_names) + ".")
    
    # Medications: list current medications (using medicationCodeableConcept text)
    medications = fhir_data.get("medications", {}).get("entry", [])
    med_names = []
    for med in medications:
        med_concept = med.get("medicationCodeableConcept", {})
        med_text = med_concept.get("text")
        if med_text:
            med_names.append(med_text)
    if med_names:
        summary_parts.append("Currently on " + ", ".join(med_names) + ".")
    
    # Observations: Focus on key labs like HbA1c (LOINC 4548-4) and/or blood glucose (e.g., LOINC 2339-0)
    observations = fhir_data.get("observations", {}).get('entry', [])
    hba1c_values = []
    for obs in observations:
        code = obs.get("code", {})
        codings = code.get("coding", [])
        for coding in codings:
            if coding.get("code") == "4548-4":
                # Assume valueQuantity holds the lab value
                value = obs.get("valueQuantity", {}).get("value")
                if value is not None:
                    hba1c_values.append(value)
    if hba1c_values:
        latest_hba1c = hba1c_values[-1]
        summary_parts.append(f"Recent HbA1c is {latest_hba1c}%.")
    else:
        summary_parts.append("No recent HbA1c or glucose monitoring data available.")
    
    # Encounters and DiagnosticReports can be used to provide context if needed.
    encounters = fhir_data.get("encounters", [])
    if encounters:
        summary_parts.append(f"{len(encounters)} recent encounter(s) available for review.")
    
    diagnostic_reports = fhir_data.get("diagnosticReports", [])
    if diagnostic_reports:
        summary_parts.append("Relevant diagnostic reports are present.")
    
    # Risk assessments (if available) can be noted
    risk_assessments = fhir_data.get("riskAssessments", [])
    if risk_assessments:
        summary_parts.append("Risk assessments data is available.")
    
    # Care plans, goals, and tasks might provide additional treatment context
    care_plans = fhir_data.get("carePlans", [])
    if care_plans:
        summary_parts.append("Current care plan details have been provided.")
    
    # Combine summary parts into a single summary string
    # Ensure the output is a plain text paragraph (no markdown formatting or bullet lists)
    clinical_summary = " ".join(summary_parts)
    
    return clinical_summary

async def create_cards(
    clinical_summary: str,
    source_url: str,
    source_label: str = 'Chronic Disease Progressive Model for Diabetes (CDPMD)',
    source_icon: str = 'https://imgs.search.brave.com/MXd2gYPBb_8uzLekNa80ujdvyMZP8a33lPsO2Cw4m7c/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly90My5m/dGNkbi5uZXQvanBn/LzAxLzg1LzY2Lzk2/LzM2MF9GXzE4NTY2/OTY0MV9STDA1UG1Y/TTgyUXBwYVJCUVZz/dXk0SkRWcnpoenNh/SC5qcGc'
) -> dict:
    return {
        'cards': [
            {
                'summary': 'Patient Summary',
                'detail': clinical_summary,
                'indicator': 'info',
                'source': Link(label=source_label, url=source_url, icon=source_icon).dict(),
                'links': [
                    CardDetailsLink(
                        label='Get AI generated predictions',
                        url=f'{source_url}launch',
                        type=CardDetailsLinkType.smart.value
                    ).dict()
                ]
            }
        ]
    }
