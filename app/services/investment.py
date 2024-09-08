from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.charity_project import CharityProject
from app.models.donation import Donation


async def mark_as_invested(obj, session: AsyncSession):
    """Отметить проект или пожертвование как полностью инвестированное."""
    obj.fully_invested = True
    obj.close_date = datetime.now()
    session.add(obj)


async def invest_in_projects(
    donation: Donation, session: AsyncSession
):
    """Инвестировать пожертвование в доступные проекты."""
    open_projects = await session.execute(
        select(
            CharityProject
        ).where(
            CharityProject.fully_invested.is_(False)
        ).order_by(CharityProject.create_date)
    )
    open_projects = open_projects.scalars().all()

    for project in open_projects:
        needed_amount = project.full_amount - project.invested_amount

        if donation.full_amount - donation.invested_amount >= needed_amount:
            project.invested_amount += needed_amount
            donation.invested_amount += needed_amount
            await mark_as_invested(project, session)
        else:
            project.invested_amount += (
                donation.full_amount - donation.invested_amount
            )
            donation.invested_amount = donation.full_amount
            break

        session.add(project)

    if donation.full_amount == donation.invested_amount:
        await mark_as_invested(donation, session)

    await session.commit()
    await session.refresh(donation)
    return donation


async def invest_in_donations(
    project: CharityProject, session: AsyncSession
):
    """Инвестировать доступные пожертвования в проект."""
    free_donations = await session.execute(
        select(
            Donation
        ).where(
            Donation.fully_invested.is_(False)
        ).order_by(Donation.create_date)
    )
    free_donations = free_donations.scalars().all()

    for donation in free_donations:
        needed_amount = project.full_amount - project.invested_amount

        if donation.full_amount - donation.invested_amount >= needed_amount:
            project.invested_amount += needed_amount
            donation.invested_amount += needed_amount
            await mark_as_invested(project, session)
        else:
            project.invested_amount += (
                donation.full_amount - donation.invested_amount
            )
            donation.invested_amount = donation.full_amount

        session.add(donation)

        if project.invested_amount == project.full_amount:
            await mark_as_invested(project, session)
            break

    await session.commit()
    await session.refresh(project)
    return project
