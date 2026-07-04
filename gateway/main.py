import httpx
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt

app = FastAPI(title="PetCloud API Gateway", description="Єдина точка входу для мікросервісів")

SECRET_KEY = "diploma_super_secret_key_change_me_later"
ALGORITHM = "HS256"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SERVICES = {
    "auth_service": "http://auth_service:8001",
    "animal_service": "http://animal_service:8002",
    "booking_service": "http://booking_service:8003"
}

@app.api_route("/{service_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def gateway(request: Request, service_path: str):
    service_path = service_path.lstrip('/')
    normalized_path = service_path.lower()
    target_service = None

    
    if normalized_path.startswith("org-info"):
        target_service = SERVICES["auth_service"]
    elif normalized_path.startswith("public/hotel"):
        target_service = SERVICES["booking_service"]
    elif (normalized_path.startswith("public/aviaries") or
          normalized_path.startswith("public/bookings") or
          normalized_path.startswith("public/services") or
          normalized_path.startswith("public/booking-requests")):
        target_service = SERVICES["booking_service"]
    elif (normalized_path.startswith("public/site") or
          normalized_path.startswith("public/animals")):
        target_service = SERVICES["animal_service"]

    if target_service is None:
        if normalized_path.startswith("api/public/"):
            public_path = service_path[len("api/public/"):]
            service_path = public_path
            if (public_path.startswith("auth/") or public_path.startswith("org/") or
                public_path.startswith("organizations") or public_path.startswith("org-info")):
                target_service = SERVICES["auth_service"]
            elif public_path.startswith("hotel/"):
                target_service = SERVICES["booking_service"]
            elif (public_path.startswith("animals") or public_path.startswith("shelter") or
                  public_path.startswith("site") or public_path.startswith("pets")):
                target_service = SERVICES["animal_service"]
            elif (public_path.startswith("bookings") or public_path.startswith("aviaries") or
                  public_path.startswith("hotel_pets") or public_path.startswith("services") or
                  public_path.startswith("settings")):
                target_service = SERVICES["booking_service"]
            else:
                target_service = SERVICES["auth_service"]

        elif service_path.startswith("auth/") or service_path in ["login", "register"]:
            target_service = SERVICES["auth_service"]

        elif (service_path.startswith("animals") or 
              service_path.startswith("inventory") or 
              service_path.startswith("medical-records") or
              service_path.startswith("tasks")):
            target_service = SERVICES["animal_service"]

        elif (service_path.startswith("bookings") or 
              service_path.startswith("aviaries") or 
              service_path.startswith("hotel_pets") or 
              service_path.startswith("hotel_tasks") or 
              service_path.startswith("booking-requests") or 
              service_path.startswith("services") or 
              service_path.startswith("settings")):
            target_service = SERVICES["booking_service"]
            if service_path.startswith("settings"):
                auth_header = request.headers.get("authorization", "")
                if auth_header.lower().startswith("bearer "):
                    token = auth_header[7:]
                    try:
                        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                        if payload.get("org_type") == "shelter":
                            target_service = SERVICES["animal_service"]
                    except JWTError:
                        pass

        else:
            raise HTTPException(status_code=404, detail=f"Шлях /{service_path} не знайдено в API Gateway")

    target_url = f"{target_service}/{service_path}"
    if request.url.query:
        target_url += f"?{request.url.query}"

    body = await request.body()
    
    headers = dict(request.headers)
    headers.pop("host", None)

    async with httpx.AsyncClient() as client:
        try:
            target_response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                timeout=60.0
            )
            
            return Response(
                content=target_response.content,
                status_code=target_response.status_code,
                headers=dict(target_response.headers)
            )
            
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503, 
                detail=f"Сервіс тимчасово недоступний: {exc}"
            )