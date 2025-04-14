import streamlit as st
import uuid
import datetime
from utils.blessing_generator import generate_blessing
from utils.upi_generator import generate_upi_link
from dal import db
import qrcode
from io import BytesIO


def get_qr_image(link):
    qr = qrcode.make(link)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    return buf


def main():
    st.set_page_config(page_title="BlessedWithKaineetam", layout="centered")

    pages = ["Create Blessing", "View Blessing", "Thank You", "Dashboard"]
    selected_page = st.sidebar.selectbox("Navigate", pages)

    st.sidebar.caption("🔍 Query Params:")
    st.sidebar.json(st.query_params)

    # --- PAGE: Create Blessing ---
    if selected_page == "Create Blessing":
        st.title("Create a Vishu Blessing")

        with st.form("create_blessing_form"):
            recipient = st.text_input("Recipient's Name")
            sender = st.text_input("Your Name")
            tone = st.selectbox("Blessing Tone", ["modern", "traditional", "funny"])
            custom_message = st.text_area("Custom Message (optional)")
            upi_id = st.text_input("Your UPI ID (for receiving Kaineetam)")
            submitted = st.form_submit_button("Generate Blessing")

            if submitted and recipient and sender and upi_id:
                bless_id = str(uuid.uuid4())[:8]
                blessing_line = generate_blessing(tone)
                bless_data = {
                    "recipient": recipient,
                    "sender": sender,
                    "tone": tone,
                    "upi": upi_id,
                    "custom_message": custom_message,
                    "blessing": blessing_line,
                    "created_at": str(datetime.datetime.now())
                }
                db.save_blessing(bless_id, bless_data)
                st.success(f"Blessing Created! Share this code: `{bless_id}`")
                st.write("**Share this link with your friend:**")
                st.code(f"?page=view&code={bless_id}")
                st.markdown(f"[Click to view it now](?page=view&code={bless_id})")

    # --- PAGE: View Blessing ---
    elif selected_page == "View Blessing":
        bless_id = st.query_params.get("code", "")
        data = db.get_blessing(bless_id)

        if not data:
            st.error("Blessing not found.")
        else:
            st.title(f"Happy Vishu, {data['recipient']}!")
            st.subheader(data['blessing'])
            if data.get("custom_message"):
                st.info(f"✉️ {data['custom_message']}")
            st.caption(f"From: {data['sender']}")
            st.markdown("---")

            st.subheader("Give Kaineetam")
            with st.form("kaineetam_form"):
                amount = st.number_input("How much would you like to give?", min_value=1, step=1)
                confirmed = st.form_submit_button("Generate UPI Link")
                if confirmed:
                    link = generate_upi_link(data['upi'], data['sender'], amount)
                    st.success("Click below to pay!")
                    st.markdown(f"[Pay Now via UPI App]({link})")
                    st.image(get_qr_image(link), caption="Scan to Pay")

            st.markdown("---")
            st.subheader("Already Paid? Let us know")
            with st.form("payment_confirmation"):
                name = st.text_input("Your Name")
                paid_amount = st.number_input("Amount Paid (₹)", min_value=1, step=1, key="log_amount")
                note = st.text_area("Optional message")
                confirm_paid = st.form_submit_button("Confirm Payment")
                if confirm_paid and name:
                    log = {
                        "name": name,
                        "amount": paid_amount,
                        "note": note,
                        "timestamp": str(datetime.datetime.now())
                    }
                    db.save_payment(bless_id, log)
                    st.success("Thank you! Your Kaineetam has been recorded.")
                    st.markdown(f"[Go to Thank You Page](?page=thankyou&code={bless_id})")

    # --- PAGE: Thank You ---
    elif selected_page == "Thank You":
        bless_id = st.query_params.get("code", "")
        data = db.get_blessing(bless_id)
        if data:
            st.title("Thank You for Your Kaineetam!")
            st.subheader("You're officially blessed this Vishu.")
            st.success(f"Blessing from {data['sender']} to {data['recipient']}")
        else:
            st.error("No record found.")

    # --- PAGE: Dashboard ---
    elif selected_page == "Dashboard":
        bless_id = st.query_params.get("code", "")
        data = db.get_blessing(bless_id)
        logs = db.get_all_payments(bless_id)

        if not data:
            st.error("Blessing not found.")
        else:
            st.title("Kaineetam Dashboard")
            st.caption(f"Blessing by {data['sender']} for {data['recipient']}")
            total = sum(p['amount'] for p in logs) if logs else 0
            st.metric("Total Kaineetam Received", f"₹{total}")
            if logs:
                top = max(logs, key=lambda x: x['amount'])
                st.info(f"Top Giver: **{top['name']}** — ₹{top['amount']}")
                st.markdown("---")
                st.subheader("All Kaineetam Received")
                for p in logs:
                    st.write(f"**{p['name']}** sent ₹{p['amount']}")
                    if p['note']:
                        st.write(f"✉️ _{p['note']}_")
                    st.caption(p['timestamp'])
                    st.markdown("---")
            else:
                st.warning("No Kaineetam received yet!")


if __name__ == "__main__":
    main()
