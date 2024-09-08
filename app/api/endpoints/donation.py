from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import AllDonations, DonationDB, DonationBase
from app.services.investment import invest_in_projects

router = APIRouter()


@router.get(
    "/",
    response_model_exclude_none=True,
    response_model=list[AllDonations],
    dependencies=[Depends(current_superuser)],
)
async def get_all_donation(session: AsyncSession = Depends(get_async_session)):
    return await donation_crud.get_multi(session)


@router.post("/", response_model=DonationDB)
async def create_donation(
    donation_in: DonationBase,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    return await invest_in_projects(
        await donation_crud.create(donation_in, session, user),
        session
    )


@router.get("/my", response_model=list[DonationDB])
async def get_user_donations(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await donation_crud.get_user_donations(user, session)
