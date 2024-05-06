from datetime import datetime
import pytz


class TimeZoneConverter:
    def __init__(self, from_tz, to_tz):

        self.from_tz = pytz.timezone(from_tz)
        self.to_tz = pytz.timezone(to_tz)

    def convert_time_gmt_to_utc(
        self, time_str, format="%a, %d %b %Y %H:%M:%S %Z", output_format="%y%m%d %H:%M"
    ):
        # A time conversion method that converts a time string in a given time zone to a time string in a specified format in another time zone.

        time_obj = datetime.strptime(
            time_str, format
        )  # Parsing a time string into a datetime object
        time_obj_from_tz = self.from_tz.localize(
            time_obj
        )  # Add source time zone information to the time object
        time_obj_to_tz = time_obj_from_tz.astimezone(
            self.to_tz
        )  # Convert the time object to the target time zone.
        return time_obj_to_tz.strftime(
            output_format
        )  # Format the time object as a string and return the converted time string.

    def format_time_slice(
        self, time_str, format="%a, %d %b %Y %H:%M:%S %Z", output_format="%y%m%d %H:%M"
    ):
        # Time conversion method to convert a given GMT time string to a time string in a specified format in the UTC+8 time zone.

        return self.convert_time_gmt_to_utc(
            time_str, format, output_format
        )  # Call the time zone converter for conversion


class SystemTime:
    @staticmethod
    def format_current_time(format_string="%m/%d %H:%M:%S"):
        time_current = datetime.now()
        return time_current.strftime(format_string)
