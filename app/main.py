import uvicorn
from fastapi import FastAPI, Query, Body, APIRouter
from fastapi.openapi.docs import get_swagger_ui_html

from app.hotels.routers import hotels_router

main_router = APIRouter(prefix='/v1')
main_router.include_router(hotels_router, tags=['Hotels'])

app = FastAPI()
app.include_router(main_router)


@main_router.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
