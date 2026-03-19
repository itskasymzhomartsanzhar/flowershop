import os
import psycopg2
from google.oauth2 import service_account
from googleapiclient.discovery import build

DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ.get("DB_HOST", "postgres")
DB_PORT = os.environ.get("DB_PORT", "5432")
SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]
SERVICE_ACCOUNT_FILE = os.environ.get("SERVICE_ACCOUNT_FILE", "/app/service_account.json")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

HEADERS = [
    "№ заказа",
    "Статус",
    "Дата и время заказа",
    "Сумма заказа",
    "Состав заказа",
    "Комментарий",
    "Время доставки",
    "Адрес доставки",
    "Телефон получателя",
    "Промокод",
    "Имя заказчика",
    "Username TG",
    "Телефон заказчика",
]

QUERY = """
SELECT
    o.id,
    o.status,
    o.order_date AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Moscow',
    o.price,
    STRING_AGG(p.name || ' x' || oi.quantity, ', ' ORDER BY p.name) AS items,
    o.comment,
    o.delivery_time_slot,
    o.delivery_address,
    o.recipient_phone,
    o.promocode,
    o.payer_name,
    u.telegram_username,
    o.payer_phone
FROM api_orders o
LEFT JOIN api_users u ON o.user_id = u.id
LEFT JOIN api_orderitem oi ON oi.order_id = o.id
LEFT JOIN api_product p ON oi.product_id = p.id
GROUP BY o.id, u.telegram_username
ORDER BY o.order_date DESC;
"""

def get_orders():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )
    cur = conn.cursor()
    cur.execute(QUERY)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    result = []
    for row in rows:
        result.append([
            str(row[0]),
            row[1] or "",
            row[2].strftime("%d.%m.%Y %H:%M") if row[2] else "",
            str(row[3]) if row[3] is not None else "",
            row[4] or "",
            row[5] or "",
            row[6] or "",
            row[7] or "",
            row[8] or "",
            row[9] or "",
            row[10] or "",
            row[11] or "",
            row[12] or "",
        ])
    return result

def sync():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()

    rows = get_orders()
    values = [HEADERS] + rows

    sheet.values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range="A1:Z100000",
    ).execute()

    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range="A1",
        valueInputOption="RAW",
        body={"values": values},
    ).execute()

    print(f"Synced {len(rows)} orders")

if __name__ == "__main__":
    sync()
