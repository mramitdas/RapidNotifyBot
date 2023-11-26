"""
NotifyMeBot.

This FastAPI application serves as the backend for the NotifyMe service.

Usage:
    - Create an instance of this FastAPI application to run the NotifyMe service.

Example:
    ```python
    from fastapi import FastAPI
    from .api.V1.api import api_router

    app = FastAPI(title="NotifyMe", docs_url="/")
    app.include_router(api_router, prefix="/api/v1")
    ```

Attributes:
    - title (str): The title of the FastAPI application, set to "NotifyMe".

    - docs_url (str): The URL path for accessing the FastAPI documentation.

    - api_router (APIRouter): The router containing the API endpoints for the NotifyMe service.

    - prefix (str): The URL prefix for the included router, set to "/api/v1".

See Also:
    - FastAPI documentation for creating applications: https://fastapi.tiangolo.com/tutorial/first-steps/

Note:
    Customize the `docs_url` parameter and any other application settings as needed.
"""

from fastapi import FastAPI

from .api.V1.api import api_router

app = FastAPI(title="NotifyMe", docs_url="/")
app.include_router(api_router, prefix="/api/v1")
