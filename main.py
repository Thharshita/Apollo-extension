from fastapi import FastAPI
from routers import excel_api, scrape
import sys
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

# def custom_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema
#     openapi_schema = get_openapi(
#         title="AIKMS",
#         version="1.0.0",
#         description="API",
#         routes=app.routes,
#     )
#     openapi_schema["openapi"] = "3.0.0"  # Explicitly set OpenAPI version
#     app.openapi_schema = openapi_schema
#     return app.openapi_schema

app = FastAPI(
    title="AIKMS",
    description="API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.openapi = custom_openapi

# app.mount("/static", StaticFiles(directory="static", html=True), name="static")
# @app.get("/aikms_docs", include_in_schema=True)
# def aikms_docs():
#     return get_swagger_ui_html(
#         openapi_url=app.openapi_url,
#         title="AI-KMS-API Docs",
#         swagger_js_url="static/swagger-ui-bundle.js",
#         swagger_css_url="static/swagger-ui.css",
#     )

# @app.get("/aikms_docs", include_in_schema=True)

# def aikms():
#     return get_swagger_ui_html(
#         openapi_url=app.openapi_url,
#         title="AI-KMS-API Docs",
#         swagger_js_url="static/swagger-ui-bundle.js",
#         swagger_css_url="static/swagger-ui.css",
#     )

app.include_router(scrape.router)
app.include_router(excel_api.router)

frontend_directory = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.isdir(frontend_directory):
    @app.get("/", include_in_schema=False)
    async def frontend_index():
        return FileResponse(os.path.join(frontend_directory, "index.html"))

    app.mount("/", StaticFiles(directory=frontend_directory, html=True), name="frontend")
