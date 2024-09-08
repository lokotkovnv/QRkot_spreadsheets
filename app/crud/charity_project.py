from typing import Optional

from sqlalchemy import select, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):
    async def get_project_id_by_name(
        self,
        project_name: str,
        session: AsyncSession,
    ) -> Optional[int]:
        return (await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )).scalars().first()

    async def get_projects_by_completion_rate(self, session: AsyncSession):
        result = await session.execute(
            select(CharityProject)
            .where(CharityProject.fully_invested.is_(True))
            .order_by(
                extract(
                    'year', CharityProject.close_date
                ) - extract('year', CharityProject.create_date),
                extract(
                    'month', CharityProject.close_date
                ) - extract('month', CharityProject.create_date),
                extract(
                    'day', CharityProject.close_date
                ) - extract('day', CharityProject.create_date)
            )
        )
        return result.scalars().all()


charity_project_crud = CRUDCharityProject(CharityProject)
