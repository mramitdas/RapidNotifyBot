"""
FastAPI APIRouter for managing contact forms.

This APIRouter includes the contact_form router from the app.api.V1.endpoints.form module.
It is intended for managing endpoints related to contact forms.

Usage:
    - Include this router in your FastAPI app by adding it to the `app.include_router()` function.

Example:
    ```python
    from fastapi import FastAPI
    from .api import api_router

    app = FastAPI()
    app.include_router(api_router, prefix="/v1", tags=["v1"])
    ```

Attributes:
    - contact_form (APIRouter): The router for handling contact form related endpoints.

    - tags (List[str]): Tags associated with this router, which can be used for documentation and grouping.

Note:
    Customize the `prefix` and `tags` parameters of the `include_router` function
    when incorporating this router into your FastAPI app.

See Also:
    - FastAPI documentation on APIRouter: https://fastapi.tiangolo.com/tutorial/bigger-applications/
"""

from fastapi import APIRouter

from app.api.V1.endpoints.form import contact_form

api_router = APIRouter()
api_router.include_router(contact_form, tags=["Contact Form"])
