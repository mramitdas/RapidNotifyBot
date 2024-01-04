"""
RapidNotifyBot FastAPI Application

This FastAPI application serves as the backend for the RapidNotify service, providing a RESTful API for notification management.

Usage:
    - Create an instance of this FastAPI application to run the RapidNotify service.

Example:
    ```python
    from fastapi import FastAPI
    from .api.V1.api import api_router

    app = FastAPI(title="RapidNotify", docs_url="/")
    app.include_router(api_router, prefix="/api/v1")
    ```

Attributes:
    - title (str): The title of the FastAPI application, set to "RapidNotify".
    - docs_url (str): The URL path for accessing the FastAPI documentation.
    - api_router (APIRouter): The router containing the API endpoints for the RapidNotify service.
    - prefix (str): The URL prefix for the included router, set to "/api/v1".

See Also:
    - FastAPI documentation for creating applications: https://fastapi.tiangolo.com/tutorial/first-steps/
"""
from api.V1.api import api_router
from fastapi import FastAPI

# Create an instance of the FastAPI application
app = FastAPI(title="RapidNotify", docs_url="/")
app.include_router(api_router, prefix="/api/v1")

# Run the FastAPI application when the script is executed
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
