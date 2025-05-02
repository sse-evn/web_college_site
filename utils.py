# utils.py
import logging
from datetime import datetime, timezone
import tzdata
import config

logger = logging.getLogger(__name__)

def escape_html(text: str) -> str:
    if text is None:
        return ""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def format_timestamp_for_display(timestamp_iso_utc: str | None) -> str:
    if timestamp_iso_utc is None:
        return "еще нет"

    try:
        dt_utc = datetime.fromisoformat(timestamp_iso_utc.replace('Z', '+00:00'))

        try:
            target_tz = tzdata.ZoneInfo(config.DISPLAY_TIMEZONE)
        except tzdata.ZoneInfoNotFoundError:
            logger.error(f"Timezone '{config.DISPLAY_TIMEZONE}' not found. Using UTC.")
            target_tz = timezone.utc

        dt_display = dt_utc.astimezone(target_tz)

        return dt_display.strftime('%Y-%m-%d %H:%M:%S')

    except ValueError as e:
        logger.error(f"Failed to parse timestamp '{timestamp_iso_utc}': {e}. Returning raw string.")
        return timestamp_iso_utc
    except Exception as e:
        logger.error(f"Error formatting timestamp '{timestamp_iso_utc}': {e}. Returning raw string.")
        return timestamp_iso_utc
