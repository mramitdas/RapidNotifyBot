from fastapi import APIRouter, HTTPException

from app.schemas.form import FormInput

contact_form = APIRouter()


@contact_form.post("/RapidNotify")
async def register_form_input(data: FormInput):
    try:
        user_dict = data.model_dump(exclude_unset=True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid filter parameter: {e}")

    return user_dict.get("data")
