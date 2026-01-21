import streamlit as st
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


def send_confirmation_email(to_email, booking_id, booking_data):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = st.secrets["BREVO_API_KEY"]

    api_client = sib_api_v3_sdk.ApiClient(configuration)
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(api_client)

    subject = "Doctor Appointment Confirmation"
    body = f"""
Hello {booking_data['name']},

Your doctor appointment has been confirmed.

Booking ID: {booking_id}
Date: {booking_data['date']}
Time: {booking_data['time']}

Thank you.
"""

    email = sib_api_v3_sdk.SendSmtpEmail(
        sender={
            "email": st.secrets["BREVO_SENDER_EMAIL"],
            "name": st.secrets["BREVO_SENDER_NAME"]
        },
        to=[{"email": to_email}],
        subject=subject,
        text_content=body
    )

    try:
        api_instance.send_transac_email(email)
    except ApiException as e:
        raise Exception(str(e))
