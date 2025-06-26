import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheet ID (replace if changed)
SHEET_ID = "1j1lm59EbEwGCe7VcUbpqQxkJnA9VcwTlARinBE6WNkU"


def get_worksheet():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file",
             "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(SHEET_ID)
    worksheet = sheet.sheet1  # Use first worksheet
    return worksheet


def sync_to_sheet(name, date, time):
    try:
        ws = get_worksheet()
        ws.append_row([name, date, time])
        print(f"☁️ Synced {name} to Google Sheet.")
    except Exception as e:
        print(f"❌ Sync failed: {e}")
