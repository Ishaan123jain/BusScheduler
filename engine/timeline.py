from datetime import datetime, timedelta


BASE_DATE = "2026-01-01"


def time_to_minutes(time_str: str) -> int:

    dt = datetime.strptime(
        f"{BASE_DATE} {time_str}",
        "%Y-%m-%d %H:%M"
    )

    midnight = datetime.strptime(
        BASE_DATE,
        "%Y-%m-%d"
    )

    return int(
        (dt - midnight).total_seconds() / 60
    )


def minutes_to_time(minutes: int) -> str:

    midnight = datetime.strptime(
        BASE_DATE,
        "%Y-%m-%d"
    )

    dt = midnight + timedelta(minutes=minutes)

    return dt.strftime("%H:%M")