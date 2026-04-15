"""
validators.py — Input validation helpers.
Call these in routes before passing data to services.
"""


def validate_predict_payload(data: dict) -> tuple[bool, str]:
    """
    Returns (is_valid, error_message).
    error_message is empty string if valid.
    """
    try:
        traffic = float(data.get("traffic_level", 3))
        if not (0 <= traffic <= 5):
            return False, "traffic_level must be between 0 and 5"

        hour = int(data.get("time_hour", 12))
        if not (0 <= hour <= 23):
            return False, "time_hour must be between 0 and 23"

        lat = float(data.get("lat", 0))
        if not (-90 <= lat <= 90):
            return False, "lat must be between -90 and 90"

        lon = float(data.get("lon", 0))
        if not (-180 <= lon <= 180):
            return False, "lon must be between -180 and 180"

    except (TypeError, ValueError) as e:
        return False, f"Invalid input type: {e}"

    return True, ""
