import json
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.modules.auth.router import router as auth_router
from app.modules.donors.router import router as donors_router
from app.modules.programs.router import router as programs_router
from app.modules.volunteers.router import router as volunteers_router
from app.modules.surveys.router import project_router, response_router
from app.shared.exceptions import AppException

app = FastAPI(
    title="NGO Platform API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def wrap_success_envelope(request: Request, call_next):
    response = await call_next(request)

    if (
        not request.url.path.startswith("/api/")
        or response.status_code >= 400
        or response.status_code == status.HTTP_204_NO_CONTENT
        or "application/json" not in response.headers.get("content-type", "")
    ):
        return response

    body = b"".join([chunk async for chunk in response.body_iterator])
    data = json.loads(body) if body else None

    headers = {
        k: v for k, v in response.headers.items() if k.lower() not in ("content-length", "content-type")
    }
    return JSONResponse(
        status_code=response.status_code,
        content={"success": True, "message": "Success", "data": data},
        headers=headers,
    )


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail, "error": exc.error_code},
        headers=exc.headers,
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail, "error": "HTTP_ERROR"},
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation failed",
            "error": "VALIDATION_ERROR",
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "message": "Internal server error", "error": "INTERNAL_ERROR"},
    )


app.include_router(auth_router, prefix="/api/v1")
app.include_router(donors_router, prefix="/api/v1")
app.include_router(programs_router, prefix="/api/v1")
app.include_router(volunteers_router, prefix="/api/v1")
app.include_router(project_router, prefix="/api/v1")
app.include_router(response_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.APP_ENV}
