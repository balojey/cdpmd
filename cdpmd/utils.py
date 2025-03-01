from typing import Literal, Union, List, Dict, Callable, Any, Tuple, Optional
import json
from functools import wraps
import hashlib
from datetime import datetime

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

from cdpmd.schemas import CDPMD_Deps, ResourceType, CDPMDAgentResponseSchema
from cdpmd.fhir_client import FHIRClient

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
                resource_id=resource_id
            )
            
            # Filter and process resources
            if isinstance(resource, list):
                patient_ref = f"Patient/{patient_id}"
                resource = await get_reference_resources(resource, patient_ref)
            
            return resource
            
        except httpx.HTTPStatusError as e:
            print(f"FHIR API error for {resource_type}: {e}")
            return None

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

def get_payload(description: str) -> str:
    """Creates a standardized JSON payload for API requests."""
    return json.dumps({
        'description': description,
    })

class AsyncCache:
    def __init__(self, ttl: Optional[float] = 300):
        """
        Args:
            ttl: Time-to-live in seconds for cache entries. 
                 None means no expiration. Default: 300s (5 minutes)
        """
        self.cache: Dict[str, Tuple[float, Any]] = {}  # (expiration, value)
        self.ttl = ttl
    
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
            
            # Execute and cache result
            result = await func(*args, **kwargs)
            expiration = time.time() + self.ttl if self.ttl else None
            self.cache[key] = (expiration, result)
            return result
            
        return wrapper
    
    def _make_key(self, args: Tuple, kwargs: Dict) -> str:
        """Create unique hash key from arguments"""
        dumped = json.dumps({
            'args': args,
            'kwargs': {
                k: v for k, v in kwargs.items() 
                if k not in ['ttl']  # Exclude TTL from key generation
            }
        }, sort_keys=True, default=str)
        return hashlib.sha256(dumped.encode()).hexdigest()
    
    def clear(self):
        """Clear all cached entries"""
        self.cache.clear()

    def set_ttl(self, ttl: Optional[float]):
        """Update TTL for new entries (does not affect existing entries)"""
        self.ttl = ttl

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