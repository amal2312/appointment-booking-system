try:
    import sib_api_v3_sdk
    from sib_api_v3_sdk.rest import ApiException
    BREVO_AVAILABLE = True
except ImportError:
    BREVO_AVAILABLE = False


def send_confirmation_email(to_email, booking_id, booking_data):
    if not BREVO_AVAILABLE:
        raise Exception("Brevo email service not available in this environment")

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = st.secrets["BREVO_API_KEY"]

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to_email}],
        sender={"email": st.secrets["BREVO_SENDER_EMAIL"]},
        subject="Doctor Appointment Confirmation",
        html_content=f"""
        <h2>Appointment Confirmed</h2>
        <p><b>Booking ID:</b> {booking_id}</p>
        <p><b>Name:</b> {booking_data['name']}</p>
        <p><b>Date:</b> {booking_data['date']}</p>
        <p><b>Time:</b> {booking_data['time']}</p>
        """
    )

    api_instance.send_transac_email(email)

