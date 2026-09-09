"""
MahaArogya — Security & Authorization Middleware
Enforces role permissions and scope boundaries on API endpoints.
Returns HTTP 403 Forbidden for unauthorized role access.
"""

from fastapi import HTTPException, status
from src.rbac.models import AuthUser, Permission, UserRole


def enforce_permission(user: AuthUser, required_permission: Permission):
    """
    Enforces that user possesses required_permission.
    Raises HTTPException 403 Forbidden if unauthorized.
    """
    if not user.has_permission(required_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access Denied: Role '{user.role.value}' does not possess permission '{required_permission.value}'."
        )


def enforce_hospital_scope(user: AuthUser, target_hospital_id: str):
    """
    Enforces that user is authorized for target_hospital_id (or has government multi-hospital scope).
    Raises HTTPException 403 Forbidden if out of scope.
    """
    if user.role == UserRole.GOVERNMENT:
        return  # Government has state-wide aggregate access

    if user.hospital_id != target_hospital_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access Denied: User is restricted to hospital '{user.hospital_id}', cannot access '{target_hospital_id}'."
        )
