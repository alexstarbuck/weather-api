import requests
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURATION ---
API_KEY = "L5XK5ZVUM6PUPKEDB36XVCHGB"
LOCATION = "Zagreb"
DAYS_BACK = 3
GOOGLE_SHEET_NAME = "weather-data-api"  # Must match your actual sheet name
CREDENTIALS_FILE = "google-credentials.json"

# --- Weather API ---
url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{LOCATION}/last{DAYS_BACK}days?unitGroup=metric&key={API_KEY}&include=days"

response = requests.get(url)
response.raise_for_status()
data = response.json()

# --- Google Sheets Auth ---
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open(GOOGLE_SHEET_NAME).sheet1  # or .worksheet('Sheet1') if renamed

# --- Read existing dates from sheet ---
existing = sheet.col_values(1)  # First column = date

# --- Only write headers if sheet is empty ---
if not existing:
    sheet.append_row(["Date", "Temp Min (°C)", "Temp Max (°C)", "Conditions"])
    existing = ["Date"]  # update variable to include the header

# --- Collect only new rows ---
rows_to_insert = []

for day in data["days"]:
    date = day["datetime"]
    if date not in existing:
        row = [
            date,
            day["tempmin"],
            day["tempmax"],
            day.get("conditions", "N/A")
        ]
        rows_to_insert.append(row)

# --- Batch insert all new rows at once ---
if rows_to_insert:
    sheet.append_rows(rows_to_insert, value_input_option='USER_ENTERED')

print("✅ Weather data added to Google Sheet.")
