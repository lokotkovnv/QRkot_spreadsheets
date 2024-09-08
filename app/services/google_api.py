from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings


FORMAT = "%Y/%m/%d %H:%M:%S"

SPREADSHEET_TEMPLATE = {
    'properties': {
        'title': 'Отчет на дату',
        'locale': 'ru_RU',
    },
    'sheets': [{
        'properties': {
            'sheetType': 'GRID',
            'sheetId': 0,
            'title': 'Лист1',
            'gridProperties': {
                'rowCount': 100,
                'columnCount': 11
            }
        }
    }]
}

TABLE_VALUES_TEMPLATE = [
    ['Отчёт от', 'Числа'],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание']
]

PERMISSIONS_TEMPLATE = {
    'type': 'user',
    'role': 'writer',
    'emailAddress': 'email'
}

UPDATE_BODY_TEMPLATE = {
    'majorDimension': 'ROWS',
    'values': 'table_values'
}


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = SPREADSHEET_TEMPLATE
    spreadsheet_body['properties']['title'] = f'Отчёт на {now_date_time}'
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheet_id = response['spreadsheetId']
    return spreadsheet_id


async def set_user_permissions(
        spreadsheet_id: str,
        wrapper_services: Aiogoogle
) -> None:
    permissions_body = PERMISSIONS_TEMPLATE
    permissions_body['emailAddress'] = settings.email
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields="id"
        ))


async def spreadsheets_update_value(
        spreadsheet_id: str,
        projects: list,
        wrapper_services: Aiogoogle
) -> None:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    table_values = TABLE_VALUES_TEMPLATE
    table_values[0][1] = now_date_time
    for project in projects:
        duration = (project.close_date - project.create_date).days
        new_row = [str(project.name), duration, str(project.description)]
        table_values.append(new_row)

    update_body = UPDATE_BODY_TEMPLATE
    update_body['values'] = table_values

    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range='A1:E30',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
