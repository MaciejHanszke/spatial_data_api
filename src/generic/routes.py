from fastapi import APIRouter

from .generic_docs import service_healthy_sample_response

generic_router = APIRouter()

@generic_router.get('/health', responses=service_healthy_sample_response)
def health():
    """
    Check the health of the service (used, for example, for ECS).

    - **status_code 200**: Service healthy.
    """
    return {"detail": "OK"}