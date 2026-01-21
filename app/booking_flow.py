import re
from datetime import datetime, date
from app.rag_pipeline import rag_tool

def reset_booking():
    return {
        "name": None,
        "email": None,
        "phone": None,
        "date": None,
        "time": None
    }


# ---------- VALIDATIONS ----------

def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


def is_valid_phone(phone: str) -> bool:
    return phone.isdigit() and len(phone) == 10


def is_valid_future_date(date_text: str) -> bool:
    try:
        entered_date = datetime.strptime(date_text, "%Y-%m-%d").date()
        return entered_date >= date.today()
    except ValueError:
        return False


def is_valid_time(time_text: str) -> bool:
    pattern = r"^(0?[1-9]|1[0-2]):[0-5][0-9]\s?(AM|PM|am|pm)$"
    return re.match(pattern, time_text) is not None


# ---------- BOOKING FLOW ----------

def handle_booking_flow(user_input, booking_data):
    user_input = user_input.strip()

    # 1️⃣ NAME
    if booking_data["name"] is None:
        booking_data["name"] = user_input
        return (
            f"👋 Welcome, **{booking_data['name']}**!\n\n"
            "📧 Please enter your **email address**."
        )

    # 2️⃣ EMAIL
    if booking_data["email"] is None:
        if not is_valid_email(user_input):
            return "❌ Invalid email address. Please enter a **valid email**."

        booking_data["email"] = user_input
        return "📞 Please enter your **10-digit phone number**."

    # 3️⃣ PHONE
    if booking_data["phone"] is None:
        if not is_valid_phone(user_input):
            return "❌ Invalid phone number. Please enter a **valid 10-digit number**."

        booking_data["phone"] = user_input
        return "📅 Please enter the **appointment date** (YYYY-MM-DD)."

    # 4️⃣ DATE
    if booking_data["date"] is None:
        if not is_valid_future_date(user_input):
            return (
                "❌ Invalid date.\n\n"
                "Please enter a **future date** in **YYYY-MM-DD** format."
            )

        booking_data["date"] = user_input
        return "⏰ Please enter the **appointment time** (e.g., 10:30 AM)."

    # 5️⃣ TIME
    if booking_data["time"] is None:
        if not is_valid_time(user_input):
            return (
                "❌ Invalid time format.\n\n"
                "Please enter time as **HH:MM AM/PM** (example: 10:30 AM)."
            )

        # Validate time is within clinic hours (9 AM to 5 PM)
        try:
            time_obj = datetime.strptime(user_input.strip(), "%I:%M %p").time()
            clinic_start = datetime.strptime("09:00 AM", "%I:%M %p").time()
            clinic_end = datetime.strptime("05:00 PM", "%I:%M %p").time()
            
            if not (clinic_start <= time_obj <= clinic_end):
                return (
                    "❌ The selected time is outside clinic hours.\n\n"
                    "📌 Clinic appointments are available between **9:00 AM and 5:00 PM**."
                )
        except ValueError:
            return (
                "❌ Could not validate time.\n\n"
                "Please enter time as **HH:MM AM/PM** (example: 10:30 AM)."
            )

        booking_data["time"] = user_input.upper()

        return (
            "✅ **Please confirm your appointment details:**\n\n"
            f"👤 **Name:** {booking_data['name']}\n"
            f"📧 **Email:** {booking_data['email']}\n"
            f"📞 **Phone:** {booking_data['phone']}\n"
            f"📅 **Date:** {booking_data['date']}\n"
            f"⏰ **Time:** {booking_data['time']}\n\n"
            "👉 Type **yes** to confirm or **no** to cancel."
        )
    return None
