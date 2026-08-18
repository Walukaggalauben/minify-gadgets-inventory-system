from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from models.system_setting import SystemSetting


DEFAULT_TIMEZONE = "Africa/Kampala"


def get_application_timezone():
    """
    Return the timezone configured in System Settings.

    Falls back to Africa/Kampala if the configured timezone
    is missing or invalid.
    """

    try:
        settings = SystemSetting.get_settings()

        timezone_name = (
            settings.timezone
            if settings and settings.timezone
            else DEFAULT_TIMEZONE
        )

    except Exception:
        timezone_name = DEFAULT_TIMEZONE

    try:
        return ZoneInfo(timezone_name)

    except Exception:
        return ZoneInfo(DEFAULT_TIMEZONE)


def utc_now():
    """
    Return the current UTC time as a timezone-aware datetime.
    """

    return datetime.now(timezone.utc)


def application_now():
    """
    Return the current datetime in the application's
    configured timezone.
    """

    return utc_now().astimezone(
        get_application_timezone()
    )

def utc_now_naive():
    """
    Return current UTC time as a naive datetime.

    Database audit timestamps in this application are stored
    as naive UTC datetimes.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def application_date():
    """
    Return today's date according to the application's
    configured timezone.
    """

    return application_now().date()