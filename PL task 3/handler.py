import re


def is_valid_email(email):
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(pattern, email) is not None


def handler(event, context):
    if not isinstance(event, dict):
        return error_response(["Invalid JSON structure"])

    event_type = event.get("type")

    if event_type == "USER_SIGNUP":
        return handle_user_signup(event)
    elif event_type == "PAYMENT":
        return handle_payment(event)
    elif event_type == "FILE_UPLOAD":
        return handle_file_upload(event)
    else:
        return error_response(["Unknown event type"])


# ---------------- USER SIGNUP ---------------- #

def handle_user_signup(event):
    errors = []

    required_fields = ["user_id", "email", "plan"]

    for field in required_fields:
        if field not in event:
            errors.append(f"Missing field: {field}")

    if errors:
        return error_response(errors)

    user_id = event["user_id"]
    email = event["email"]
    plan = event["plan"]

    if not isinstance(user_id, int):
        errors.append("user_id must be int")

    if not isinstance(email, str) or not is_valid_email(email):
        errors.append("Invalid email")

    if not isinstance(plan, str) or plan.lower() not in ["free", "pro", "edu"]:
        errors.append("Invalid plan")

    if errors:
        return error_response(errors)

    email = email.lower()
    plan = plan.lower()

    return {
        "status": "ok",
        "message": "Signup processed",
        "data": {
            "user_id": user_id,
            "email": email,
            "plan": plan,
            "welcome_email_subject": f"Welcome to the {plan} plan!"
        },
        "errors": []
    }


# ---------------- PAYMENT ---------------- #

def handle_payment(event):
    errors = []

    required_fields = ["payment_id", "user_id", "amount", "currency"]

    for field in required_fields:
        if field not in event:
            errors.append(f"Missing field: {field}")

    if errors:
        return error_response(errors)

    payment_id = event["payment_id"]
    user_id = event["user_id"]
    amount = event["amount"]
    currency = event["currency"]

    if not isinstance(payment_id, str):
        errors.append("payment_id must be string")

    if not isinstance(user_id, int):
        errors.append("user_id must be int")

    if not isinstance(amount, (int, float)) or amount <= 0:
        errors.append("amount must be positive number")

    if not isinstance(currency, str) or currency.upper() not in ["BHD", "USD", "EUR"]:
        errors.append("Invalid currency")

    if errors:
        return error_response(errors)

    currency = currency.upper()
    amount = round(float(amount), 3)

    fee = round(amount * 0.02, 3)
    net_amount = round(amount - fee, 3)

    return {
        "status": "ok",
        "message": "Payment processed",
        "data": {
            "payment_id": payment_id,
            "user_id": user_id,
            "amount": amount,
            "currency": currency,
            "fee": fee,
            "net_amount": net_amount
        },
        "errors": []
    }


# ---------------- FILE UPLOAD ---------------- #

def handle_file_upload(event):
    errors = []

    required_fields = ["file_name", "size_bytes", "bucket", "uploader"]

    for field in required_fields:
        if field not in event:
            errors.append(f"Missing field: {field}")

    if errors:
        return error_response(errors)

    file_name = event["file_name"]
    size_bytes = event["size_bytes"]
    bucket = event["bucket"]
    uploader = event["uploader"]

    if not isinstance(file_name, str):
        errors.append("file_name must be string")

    if not isinstance(size_bytes, int) or size_bytes < 0:
        errors.append("size_bytes must be >= 0")

    if not isinstance(bucket, str):
        errors.append("bucket must be string")

    if not isinstance(uploader, str) or not is_valid_email(uploader):
        errors.append("Invalid uploader email")

    if errors:
        return error_response(errors)

    file_name = file_name.strip()
    bucket = bucket.lower()
    uploader = uploader.lower()

    if size_bytes < 1_000_000:
        storage_class = "STANDARD"
    elif size_bytes < 50_000_000:
        storage_class = "STANDARD_IA"
    else:
        storage_class = "GLACIER"

    return {
        "status": "ok",
        "message": "Upload processed",
        "data": {
            "file_name": file_name,
            "size_bytes": size_bytes,
            "bucket": bucket,
            "uploader": uploader,
            "storage_class": storage_class
        },
        "errors": []
    }


# ---------------- ERROR RESPONSE ---------------- #

def error_response(errors):
    return {
        "status": "error",
        "message": "Validation failed",
        "data": {},
        "errors": errors
    }
