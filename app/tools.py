from app.rag_pipeline import rag_tool
from db.database import save_booking
from utils.email_utils import send_confirmation_email


def rag_search_tool(query):
    return rag_tool(query)


def booking_persistence_tool(booking_data):
    booking_id = save_booking(booking_data)
    return {"success": True, "booking_id": booking_id}


def email_tool(to_email, booking_id, booking_data):
    try:
        send_confirmation_email(to_email, booking_id, booking_data)
        return {"success": True}
    except Exception:
        return {"success": False}
