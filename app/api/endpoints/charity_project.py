from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_charity_project_closed_or_invested,
    check_charity_project_exists,
    check_charity_project_fully_invested,
    check_name_duplicate,
    check_full_amount_validity
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import (
    CharityProjectDB,
    CharityProjectUpdate,
    CharityProjectCreate,
)
from app.services.investment import invest_in_donations

router = APIRouter()


@router.post(
    "/", response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def create_new_project(
    project_in: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    await check_name_duplicate(project_in.name, session)
    return await invest_in_donations(
        await charity_project_crud.create(project_in, session),
        session
    )


@router.get(
    "/",
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_projects(
    session: AsyncSession = Depends(get_async_session),
):
    return await charity_project_crud.get_multi(session)


@router.delete(
    "/{project_id}",
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def delete_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    await check_charity_project_closed_or_invested(
        await check_charity_project_exists(project_id, session)
    )
    return await charity_project_crud.remove(
        await check_charity_project_exists(project_id, session), session
    )


@router.patch(
    "/{project_id}",
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def update_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    await check_name_duplicate(obj_in.name, session)
    charity_project = await check_charity_project_exists(project_id, session)

    await check_charity_project_fully_invested(charity_project)

    if obj_in.full_amount is not None:
        await check_full_amount_validity(charity_project, obj_in.full_amount)

    return await charity_project_crud.update(charity_project, obj_in, session)
