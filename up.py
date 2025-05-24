import streamlit as st
import uuid
import datetime
from io import BytesIO
from typing import Dict, Any, List, Optional
import pandas as pd
import qrcode

# --- Constants ---
PAGE_CREATE = "Create Blessing"
PAGE_VIEW = "View Blessing"
PAGE_THANK_YOU = "Thank You"
PAGE_DASHBOARD = "Dashboard"
APP_TITLE = "BlessedWithKaineetam ✨"

# --- Mock implementations for demonstration ---
class MockDB:
    """ A simple in-memory mock database using Streamlit's session state """
    def __init__(self):
        if 'mock_db_blessings' not in st.session_state:
            st.session_state.mock_db_blessings = {}  # {bless_id: data}
        if 'mock_db_payments' not in st.session_state:
            st.session_state.mock_db_payments = {}  # {bless_id: [payment_log]}

    def save_blessing(self, bless_id: str, data: Dict[str, Any]):
        st.session_state.mock_db_blessings[bless_id] = data
        if bless_id not in st.session_state.mock_db_payments:
            st.session_state.mock_db_payments[bless_id] = []
        print(f"Saved Blessing {bless_id}: {data}")  # Debug print

    def get_blessing(self, bless_id: str) -> Optional[Dict[str, Any]]:
        return st.session_state.mock_db_blessings.get(bless_id)

    def save_payment(self, bless_id: str, log: Dict[str, Any]):
        if bless_id in st.session_state.mock_db_payments:
            st.session_state.mock_db_payments[bless_id].append(log)
            print(f"Saved Payment for {bless_id}: {log}")  # Debug print
        else:
            print(f"Error: Could not find payment log for blessing ID {bless_id}")

    def get_all_payments(self, bless_id: str) -> List[Dict[str, Any]]:
        payments = st.session_state.mock_db_payments.get(bless_id, [])
        for p in payments:
            if 'amount' in p and not isinstance(p['amount'], (int, float)):
                try:
                    p['amount'] = float(p['amount'])
                except (ValueError, TypeError):
                    p['amount'] = 0
        return payments

# Instantiate the mock DB
db = MockDB()

def generate_blessing(tone: str) -> str:
    """ Mock function to generate a blessing. """
    blessings = {
        "modern": "Wishing you a sparkling Vishu filled with joy and prosperity! ✨",
        "traditional": "May this Vishu bring abundance, happiness, and peace to your home. Heartfelt wishes!",
        "funny": "Hope your Vishu is as bright as the കണിക്കൊന്ന and your Kaineetam is heavier than a jackfruit! 😄",
        "poetic": "Like the golden Kani blooms, may your life blossom with success and fortune this Vishu.",
        "simple": "Happy Vishu! Wishing you the very best."
    }
    return blessings.get(tone, blessings["modern"])

def generate_upi_link(upi_id: str, recipient_name: str, amount: float) -> str:
    """ Mock function to generate a UPI link. """
    return f"upi://pay?pa={upi_id}&pn={recipient_name.replace(' ', '%20')}&am={amount:.2f}&cu=INR&tn=Vishu%20Kaineetam"

# --- Image Constants ---
# Assumes an 'images' subfolder. If you don't have it, image selection will show a warning.
IMAGE_FOLDER = "images/"
VISHU_IMAGES = {
    "Kani Konna (Golden Shower)": IMAGE_FOLDER + "vishu_konna.png",
    "Vishu Kani Arrangement": IMAGE_FOLDER + "vishu_kani.png",
    "Vishu Sadya (Feast)": IMAGE_FOLDER + "vishu_sadya.png",
    "Fireworks (Padakkam)": IMAGE_FOLDER + "vishu_padakkam.png",
    "None": None
}
VISHU_IMAGE_OPTIONS = list(VISHU_IMAGES.keys())

# --- Helper Functions ---

# CORRECTED: This function now has its proper implementation.
def get_qr_image(link: str) -> BytesIO:
    """Generates a QR code image from a link."""
    qr = qrcode.make(link)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)
    return buf

def get_blessing_data(bless_id: Optional[str]) -> Optional[Dict[str, Any]]:
    """Safely fetches blessing data."""
    if not bless_id:
        st.error("No Blessing ID provided.")
        return None
    try:
        with st.spinner("Loading Blessing..."):
            data = db.get_blessing(bless_id)
        if not data:
            st.error(f"Blessing with ID `{bless_id}` not found. Please check the code.")
            return None
        return data
    except Exception as e:
        st.error(f"An error occurred while fetching the blessing: {e}")
        return None

def get_payment_logs(bless_id: Optional[str]) -> List[Dict[str, Any]]:
    """Safely fetches payment logs."""
    if not bless_id:
        return []
    try:
        return db.get_all_payments(bless_id)
    except Exception as e:
        st.error(f"An error occurred while fetching payment logs: {e}")
        return []

# --- Page Implementations ---

def page_create_blessing():
    """Handles the 'Create Blessing' page."""
    st.header("🌸 Create Your Vishu Blessing")
    st.markdown("Fill in the details below to generate a unique Vishu blessing link to share with your loved ones and receive Kaineetam digitally!")

    with st.form("create_blessing_form"):
        col1, col2 = st.columns(2)
        with col1:
            recipient = st.text_input("Recipient's Name*", help="Who is this blessing for?")
            sender = st.text_input("Your Name*", help="Who is sending this blessing?")
            upi_id = st.text_input("Your UPI ID*", help="Enter your UPI ID (e.g., yourname@bank) to receive Kaineetam.")

        with col2:
            tone_options = ["modern", "traditional", "funny", "poetic", "simple"]
            tone = st.selectbox("Select Blessing Tone*", tone_options, help="Choose the style of the blessing message.")
            image_choice = st.selectbox("Choose an Image (optional)", VISHU_IMAGE_OPTIONS, index=len(VISHU_IMAGE_OPTIONS)-1, help="Select a Vishu-themed image.")
            custom_message = st.text_area("Add a Custom Message (optional)", max_chars=200, help="Add a personal note.")

        submitted = st.form_submit_button("✨ Generate Blessing Link")

        if submitted:
            missing_fields = []
            if not recipient: missing_fields.append("Recipient's Name")
            if not sender: missing_fields.append("Your Name")
            if not upi_id: missing_fields.append("Your UPI ID")

            if missing_fields:
                st.warning(f"Please fill in the required fields: {', '.join(missing_fields)}")
            else:
                with st.spinner("Generating your blessing..."):
                    bless_id = str(uuid.uuid4())[:8]
                    blessing_line = generate_blessing(tone)
                    selected_image_path = VISHU_IMAGES.get(image_choice)

                    bless_data = {
                        "recipient": recipient.strip(),
                        "sender": sender.strip(),
                        "tone": tone,
                        "upi": upi_id.strip(),
                        "custom_message": custom_message.strip(),
                        "blessing": blessing_line,
                        "image_path": selected_image_path,
                        "created_at": str(datetime.datetime.now()),
                        "code": bless_id
                    }
                    try:
                        db.save_blessing(bless_id, bless_data)
                        st.success("✅ Blessing Created Successfully!")
                        st.balloons()

                        st.markdown("---")
                        st.subheader("Share this Blessing:")
                        st.markdown(f"You can share the **Blessing Code** or the **Direct Link** with **{recipient}**.")

                        st.markdown("**Blessing Code:**")
                        st.code(bless_id, language=None)

                        # Note: This creates a relative URL. For sharing externally, you'd need the full domain.
                        view_link = f"/?page={PAGE_VIEW}&code={bless_id}"
                        st.markdown("**Direct Link:**")
                        st.code(view_link, language=None)

                        st.markdown("👇 Or click here to preview it yourself:")
                        st.link_button("Preview Blessing", url=view_link)

                        dashboard_link = f"/?page={PAGE_DASHBOARD}&code={bless_id}"
                        st.markdown("---")
                        st.markdown("📈 **Track Received Kaineetam:**")
                        st.markdown(f"Use the **Blessing Code (`{bless_id}`)** or the link below to access your dashboard later.")
                        st.link_button("Go to My Kaineetam Dashboard", url=dashboard_link)

                    except Exception as e:
                        st.error(f"Failed to save blessing: {e}")

def page_view_blessing():
    """Handles the 'View Blessing' page."""
    st.header("🎁 A Vishu Blessing For You!")
    bless_id = st.query_params.get("code")
    data = get_blessing_data(bless_id)

    if data:
        st.title(f"Happy Vishu, {data['recipient']}!")

        if data.get("image_path"):
            try:
                # In a real app, you'd check if the file exists. For this demo, we assume it does.
                st.image(data['image_path'], use_column_width=True)
            except Exception as e:
                st.warning(f"Could not load the selected image. The path '{data['image_path']}' might be invalid.")

        st.subheader(f"📜 {data['blessing']}")
        if data.get("custom_message"):
            st.info(f"**A Personal Note from {data['sender']}:**\n\n> _{data['custom_message']}_")
        st.caption(f"Sent with love by: **{data['sender']}**")
        st.markdown("---")

        st.subheader("💝 Give Kaineetam")
        st.markdown(f"If you'd like to send some Vishu Kaineetam to {data['sender']}, you can do so easily via UPI!")

        with st.expander("💸 Send Kaineetam via UPI", expanded=True):
            # Initialize session state keys safely
            if 'kaineetam_amount' not in st.session_state:
                st.session_state.kaineetam_amount = 51.0
            if 'upi_link' not in st.session_state:
                st.session_state.upi_link = None
            if 'qr_image' not in st.session_state:
                st.session_state.qr_image = None

            st.write("**Quick Amounts (₹):**")
            cols = st.columns(4)
            suggested_amounts = [51, 101, 201, 501]
            for i, amt in enumerate(suggested_amounts):
                if cols[i].button(f"₹{amt}"):
                    st.session_state.kaineetam_amount = float(amt)
                    # Clear old QR code when amount changes
                    st.session_state.upi_link = None
                    st.session_state.qr_image = None
                    st.rerun()

            with st.form("kaineetam_form"):
                amount = st.number_input(
                    "Enter Amount (₹):",
                    min_value=1.0, step=1.0, format="%.2f",
                    key='kaineetam_amount'
                )
                generate_pressed = st.form_submit_button("Generate UPI Link / QR Code")

                if generate_pressed and amount >= 1:
                    with st.spinner("Generating payment details..."):
                        try:
                            link = generate_upi_link(data['upi'], data['sender'], float(amount))
                            qr_img = get_qr_image(link)
                            st.session_state.upi_link = link
                            st.session_state.qr_image = qr_img
                            st.success("✅ UPI Link & QR Code Generated!")
                        except Exception as e:
                            st.error(f"Could not generate UPI details: {e}")
                            st.session_state.upi_link = None
                            st.session_state.qr_image = None

            if st.session_state.upi_link and st.session_state.qr_image:
                st.markdown(f"**Click the link below (on mobile) or scan the QR code using your UPI app to pay ₹{st.session_state.kaineetam_amount:.2f} to {data['sender']}.**")
                st.markdown(f"➡️ [**Pay ₹{st.session_state.kaineetam_amount:.2f} Now via UPI App**]({st.session_state.upi_link})")
                st.image(st.session_state.qr_image, caption="Scan this QR Code to Pay")
                st.info("After completing the payment, please confirm below.")

        st.markdown("---")
        st.subheader("✍️ Confirm Your Kaineetam (Optional)")
        st.markdown("Paid already? Let the sender know by confirming your contribution below.")

        with st.expander("✅ Confirm Payment Details"):
            with st.form("payment_confirmation"):
                giver_name = st.text_input("Your Name*", help="Your name, so the sender knows who sent the Kaineetam.")
                default_paid_amount = st.session_state.kaineetam_amount if st.session_state.upi_link else 1.0
                paid_amount = st.number_input(
                    "Amount Paid (₹)*",
                    min_value=1.0, step=1.0, format="%.2f",
                    value=default_paid_amount, key="log_amount"
                )
                note = st.text_area("Optional message to sender:", max_chars=150)
                confirm_paid_pressed = st.form_submit_button("Confirm Kaineetam Sent")

                if confirm_paid_pressed:
                    if not giver_name:
                        st.warning("Please enter your name.")
                    elif not paid_amount or paid_amount < 1:
                        st.warning("Please enter a valid amount.")
                    else:
                        with st.spinner("Recording your Kaineetam..."):
                            log = {
                                "name": giver_name.strip(),
                                "amount": float(paid_amount),
                                "note": note.strip(),
                                "timestamp": str(datetime.datetime.now())
                            }
                            try:
                                db.save_payment(bless_id, log)
                                st.success("Thank you! Your Kaineetam has been recorded.")
                                st.balloons()
                                st.session_state.upi_link = None
                                st.session_state.qr_image = None

                                # Navigate to Thank You page using query params and rerun
                                st.query_params._set("page", PAGE_THANK_YOU)
                                st.query_params._set("code", bless_id)
                                st.rerun()

                            except Exception as e:
                                st.error(f"Failed to record payment: {e}")

def page_thank_you():
    """Handles the 'Thank You' page after payment confirmation."""
    st.header("🎉 Thank You!")
    st.balloons()
    bless_id = st.query_params.get("code")
    data = get_blessing_data(bless_id)

    if data:
        st.success(f"Your Kaineetam for **{data['recipient']}** from **{data['sender']}** has been successfully recorded.")
        st.markdown(f"You're officially blessed this Vishu by {data['sender']}!")
        st.info("We hope you have a wonderful and prosperous Vishu!")
    else:
        st.warning("Could not retrieve blessing details, but thank you for your confirmation!")

def page_dashboard():
    """Handles the Kaineetam tracking 'Dashboard' page."""
    st.header("📊 Kaineetam Dashboard")
    st.markdown("Track the Kaineetam received for your blessing.")

    bless_id_from_query = st.query_params.get("code")
    bless_id_input = st.text_input("Enter Blessing Code:", value=bless_id_from_query or "", max_chars=8, help="Enter the 8-character code you received when you created the blessing.")

    if not bless_id_input:
        st.info("Enter your Blessing Code to view the dashboard.")
        return

    data = get_blessing_data(bless_id_input)

    if data:
        st.subheader("Blessing Details:")
        st.markdown(f"**Recipient:** {data['recipient']}")
        st.markdown(f"**Sender (You):** {data['sender']}")
        st.markdown(f"**Blessing Code:** `{data['code']}`")
        st.markdown("---")
        st.subheader("Received Kaineetam Summary:")

        logs = get_payment_logs(bless_id_input)

        if logs:
            total_amount = sum(p.get('amount', 0) for p in logs)
            num_gifts = len(logs)
            average_amount = total_amount / num_gifts if num_gifts > 0 else 0
            try:
                top_giver = max(logs, key=lambda x: x.get('amount', 0))
            except ValueError:
                top_giver = None

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Kaineetam", f"₹{total_amount:.2f}")
            col2.metric("Number of Gifts", f"{num_gifts}")
            col3.metric("Average Gift", f"₹{average_amount:.2f}")

            if top_giver:
                st.success(f"🏆 **Top Giver:** {top_giver['name']} (₹{top_giver.get('amount', 0):.2f})")

            st.markdown("---")
            st.subheader("Detailed Log:")

            df_logs = pd.DataFrame(logs)
            df_logs = df_logs[['timestamp', 'name', 'amount', 'note']]
            df_logs['amount'] = pd.to_numeric(df_logs['amount'], errors='coerce').fillna(0)
            try:
                df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                pass # Keep original timestamp if format is unexpected
            df_logs = df_logs.sort_values(by='timestamp', ascending=False)
            df_logs.rename(columns={'name': 'Giver Name', 'amount': 'Amount (₹)', 'note': 'Message', 'timestamp': 'Time Received'}, inplace=True)

            st.dataframe(df_logs, use_container_width=True, hide_index=True)

            st.markdown("---")
            csv = df_logs.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Log as CSV",
                data=csv,
                file_name=f'kaineetam_log_{bless_id_input}.csv',
                mime='text/csv',
            )
        else:
            st.warning("💸 No Kaineetam received or recorded yet!")
            st.markdown("Share your blessing link or code to start receiving!")

# --- Main App Logic ---
def main():
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🌸",
        layout="centered",
        initial_sidebar_state="expanded"
    )

    st.sidebar.title(APP_TITLE)
    st.sidebar.markdown("Create & Share Digital Vishu Blessings")

    query_params = st.query_params
    default_page_name = query_params.get("page", PAGE_CREATE)

    page_options = {
        "🏠 Create Blessing": PAGE_CREATE,
        "🎁 View Blessing": PAGE_VIEW,
        "🙏 Thank You": PAGE_THANK_YOU,
        "📊 Dashboard": PAGE_DASHBOARD
    }

    page_titles = list(page_options.keys())
    page_names = list(page_options.values())

    try:
        default_index = page_names.index(default_page_name)
    except ValueError:
        default_index = 0

    selected_page_display = st.sidebar.radio(
        "Navigation",
        options=page_titles,
        index=default_index,
        key="page_selector"
    )

    selected_page = page_options[selected_page_display]

    with st.sidebar.expander("🔍 Query Params (for debugging)"):
        st.json(query_params.to_dict())

    if selected_page == PAGE_CREATE:
        page_create_blessing()
    elif selected_page == PAGE_VIEW:
        page_view_blessing()
    elif selected_page == PAGE_THANK_YOU:
        page_thank_you()
    elif selected_page == PAGE_DASHBOARD:
        page_dashboard()
    else:
        st.error("Page not found!")

    st.sidebar.markdown("---")
    st.sidebar.info(f"Happy Vishu! from Thiruvananthapuram.\n\n{datetime.date.today().strftime('%B %d, %Y')}")
    st.markdown("---")
    st.caption("Built with Streamlit for a Digital Vishu")

if __name__ == "__main__":
    main()