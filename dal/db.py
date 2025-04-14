from tinydb import TinyDB, Query
import os

# DB paths
BLESSINGS_DB = 'data/blessings.json'
PAYMENTS_DB = 'data/payments.json'

# Create directories if not exist
os.makedirs('data', exist_ok=True)

# Initialize TinyDB
blessings_db = TinyDB(BLESSINGS_DB)
payments_db = TinyDB(PAYMENTS_DB)


# --- Blessings ---
def save_blessing(bless_id, data):
    blessings_db.insert({'id': bless_id, **data})


def get_blessing(bless_id):
    Blessing = Query()
    result = blessings_db.get(Blessing.id == bless_id)
    return result


# --- Payments ---
def save_payment(bless_id, payment_data):
    payments_db.insert({'bless_id': bless_id, **payment_data})


def get_all_payments(bless_id):
    Payment = Query()
    return payments_db.search(Payment.bless_id == bless_id)
