from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.sql.functions import user

admin_scheme = HTTPBearer()

# TODO
def has_role(role: str):
    def _has_role(credentials: HTTPAuthorizationCredentials = Security(admin_scheme)):
        if not credentials:
            raise HTTPException(
                status_code=403, detail="No se proporcionó un token de autenticación"
            )
        # Aquí puede agregar su lógica para verificar si el usuario tiene el rol especificado
        if user.role != role:
            raise HTTPException(status_code=403, detail=f"Se requiere el rol {role}")
        return credentials

    return _has_role
