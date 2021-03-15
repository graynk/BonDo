from astral import LocationInfo
from astral.sun import sun
import pytz
from datetime import datetime, timedelta

format_string = '{} {}'
EBAT_SHABBAT = 'ебать, шаббат'
FUCK_SHABBAT_IS_OVER = 'бля шаббат кончился'

tz = pytz.timezone('Asia/Jerusalem')
city = LocationInfo('Jerusalem', 'Israel', tz.zone, 31.47, 35.13)


def calculate_shabbat(now: datetime) -> str:
    days_left = 4 - now.weekday()
    if days_left == -1:
        shabbat_end = sun(city.observer, date=now, tzinfo=city.timezone)['sunset']
        if shabbat_end > now:
            return EBAT_SHABBAT
        else:
            return FUCK_SHABBAT_IS_OVER

    if days_left < 0:
        days_left += 7
    next_friday = now + timedelta(days=days_left)
    shabbat_start = sun(city.observer, date=next_friday, tzinfo=city.timezone)['sunset']
    td = shabbat_start - now
    if td.days == 0 and td.seconds == 0:
        return EBAT_SHABBAT
    return format_timedelta(td)


def format_timedelta(td: timedelta) -> str:
    days, hours, minutes, seconds = td.days, td.seconds // 3600, (td.seconds // 60) % 60, td.seconds
    days_str = hours_str = minutes_str = seconds_str = None

    if days != 0:
        days_str = format_days(days)
    if hours != 0:
        hours_str = format_hours(hours)
    if minutes != 0:
        minutes_str = format_minutes(minutes)
    if hours == 0 and minutes == 0 and seconds != 0:
        seconds_str = format_seconds(seconds)

    return 'через {}'.format(' '.join(filter(None, [days_str, hours_str, minutes_str, seconds_str])))


def format_days(days: int) -> str:
    return format_time_unit(days, 'день', 'дня', 'дней')


def format_hours(hours: int) -> str:
    return format_time_unit(hours, 'час', 'часа', 'часов')


def format_minutes(minutes: int) -> str:
    return format_time_unit(minutes, 'минуту', 'минуты', 'минут')


def format_seconds(seconds: int) -> str:
    return format_time_unit(seconds, 'секунду', 'секунды', 'секунд')


def format_time_unit(value: int, single: str, several: str, many: str) -> str:
    last_digit = value % 10
    if last_digit == 1 and value != 11:
        return format_string.format(value, single)
    elif 2 <= last_digit < 5 and not 12 <= value < 22:
        return format_string.format(value, several)
    return format_string.format(value, many)
