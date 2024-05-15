from datetime import datetime
import pytz


class TimeZoneConverter:

    def __init__(self, from_tz, to_tz):
        # 初始化方法，設定資訊來源的時區'from_tz'和目的地時區'to_tz'，並將這兩個時區物件保留在物件的屬性中
        self.from_tz = pytz.timezone(from_tz)
        self.to_tz = pytz.timezone(to_tz)
        pass

    def convert_time_gmt_to_utc(
        self,
        time_str,
        format="%a, %d %b %Y %H:%M:%S %Z",
        output_format="%Y/%m/%d %H:%M:%S",
    ):
        # 將來源時區的時間字串轉換為目的地時區的時間字串
        time_obj = datetime.strptime(time_str, format)  # 將時間字串解析為datetime物件
        time_obj_from_tz = self.from_tz.localize(time_obj)  # 為時間物件增加來源時區資訊
        time_obj_to_tz = time_obj_from_tz.astimezone(
            self.to_tz
        )  # 將時間物件轉換為目的地時區
        return time_obj_to_tz.strftime(
            output_format
        )  # 將時間物件格式化為字串，並返回轉換後的時間字串

    def format_time_slice(
        self,
        time_str,
        format="%a, %d %b %Y %H:%M:%S %Z",
        output_format="%Y%m%d %H:%M:%S",
    ):
        # 用來將給定的GMT時間字串轉換為在UTC+8時區的特定格式時間字串
        return self.convert_time_gmt_to_utc(
            time_str, format, output_format
        )  # 呼叫時區轉換器進行轉換


class SystemTime:

    @ staticmethod
    def format_current_time(format_string="%Y/%m/%d %H:%M:%S"):
        time_current = datetime.now()
        return time_current.strftime(format_string)
