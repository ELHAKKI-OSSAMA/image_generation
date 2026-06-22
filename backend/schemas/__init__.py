from .organization import OrganizationResponse
from .auth import UserResponse

# Rebuild in dependency order
OrganizationResponse.model_rebuild()
UserResponse.model_rebuild()