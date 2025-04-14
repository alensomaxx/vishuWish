import urllib.parse

def generate_upi_link(upi_id, name, amount):
    if not (upi_id and name and amount):
        return None
    return f"upi://pay?pa={upi_id}&pn={urllib.parse.quote(name)}&am={amount}&cu=INR"
