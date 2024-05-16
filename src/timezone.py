from datetime import datetime
from zoneinfo import ZoneInfo

from aiocache import cached


class TimeZoneConverter:

    from_tz = ZoneInfo('GMT')
    to_tz = ZoneInfo('Asia/Taipei')

    @cached(ttl=3600)
    async def convert_time(self, time_str: str, format: str = "%a, %d %b %Y %H:%M:%S %Z", output_format: str = "%Y/%m/%d %H:%M:%S") -> str:
        try:
            time_obj = datetime.strptime(
                time_str, format).replace(tzinfo=self.from_tz)
            return time_obj.astimezone(self.to_tz).strftime(output_format)
        except ValueError as e:
            raise ValueError(f"時間格式錯誤: {e}")


async def get_formatted_current_time(format_string: str = "%Y/%m/%d %H:%M:%S") -> str:
    return datetime.now().strftime(format_string)
