# # import gspread
# # from oauth2client.service_account import ServiceAccountCredentials

# # scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# # creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
# # client = gspread.authorize(creds)

# # # Open your sheet
# # sheet = client.open("SchoolData")  # Name of your Google Sheet

# # def get_homework(class_, section, date):
# #     worksheet = sheet.worksheet("Homework")
# #     records = worksheet.get_all_records()

# #     result = []
# #     for row in records:
# #         if (str(row["Class"]).strip() == str(class_).strip() and 
# #             str(row["Section"]).strip().upper() == section.upper() and 
# #             row["Date"].strip() == date.strip()):
# #             result.append(f"{row['Subject']}: {row['Homework']}")
# #     return result

# # def get_timetable(class_, section, day):
# #     worksheet = sheet.worksheet("Timetable")
# #     records = worksheet.get_all_records()

# #     for row in records:
# #         if (str(row["Class"]).strip() == str(class_).strip() and 
# #             str(row["Section"]).strip().upper() == section.upper() and 
# #             row["Day"].strip().lower() == day.lower()):
# #             del row["Class"]
# #             del row["Section"]
# #             del row["Day"]
# #             return row
# #     return {}
# # sheets_service.py
# # sheets_service.py

# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# import datetime

# scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# creds = ServiceAccountCredentials.from_json_keyfile_name("/etc/secrets/credentials.json", scopes=scope)

# client = gspread.authorize(creds)

# sheet = client.open("SchoolData")

# def get_class_by_name(name):
#     data = sheet.worksheet("StudentData").get_all_records()
#     for row in data:
#         if str(row["Name"]).strip().lower() == name.strip().lower():
#             return row["Class"].strip().upper()
#     return None

# def get_timetable(class_name, day):
#     records = sheet.worksheet("Timetable").get_all_records()
#     for row in records:
#         if row["Class"].strip().upper() == class_name and row["Day"].strip().lower() == day.lower():
#             periods = [f"{k}: {v}" for k, v in row.items() if k not in ["Class", "Day"]]
#             return f"📘 Timetable for {class_name} on {day}:\n" + "\n".join(periods)
#     return f"❌ No timetable found for {class_name} on {day}."

# def get_homework(class_name, date):
#     records = sheet.worksheet("Homework").get_all_records()
#     homework_today = [row for row in records if str(row["Class"]).strip().upper() == class_name and str(row["Date"]) == date]
    
#     if not homework_today:
#         return f"📚 No homework found for {class_name} on {date}."

#     response = f"📚 Homework for {class_name} on {date}:\n"
#     for hw in homework_today:
#         response += f"- {hw['Subject']}: {hw['Homework']}\n"
#     return response.strip()
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import logging

logging.basicConfig(level=logging.INFO)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Dynamically set the credentials path
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", r"C:\Users\Vishesh\OneDrive\Desktop\edubot\credentials.json")

try:
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("SchoolData")
except FileNotFoundError:
    logging.error(f"Credentials file not found at: {CREDENTIALS_PATH}")
    raise

def get_class_by_name(name):
    try:
        data = sheet.worksheet("StudentData").get_all_records()
        for row in data:
            if str(row["Name"]).strip().lower() == name.strip().lower():
                logging.info(f"Found class {row['Class']} for name {name}")
                return row["Class"].strip().upper()
        logging.warning(f"No class found for name: {name}")
        return None
    except Exception as e:
        logging.error(f"Google Sheets error: {str(e)}")
        return None

def get_timetable(class_name, day):
    records = sheet.worksheet("Timetable").get_all_records()
    for row in records:
        if row["Class"].strip().upper() == class_name and row["Day"].strip().lower() == day.lower():
            periods = [f"{k}: {v}" for k, v in row.items() if k not in ["Class", "Day"]]
            return f"📘 Timetable for {class_name} on {day}:\n" + "\n".join(periods)
    return f"❌ No timetable found for {class_name} on {day}."

def get_homework(class_name, date):
    records = sheet.worksheet("Homework").get_all_records()
    homework_today = [row for row in records if str(row["Class"]).strip().upper() == class_name and str(row["Date"]) == date]
    
    if not homework_today:
        return f"📚 No homework found for {class_name} on {date}."
    response = f"📚 Homework for {class_name} on {date}:\n"
    for hw in homework_today:
        response += f"- {hw['Subject']}: {hw['Homework']}\n"
    return response.strip()