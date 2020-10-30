import times
import json
import options
import times
import timezones
import strutils

const formatString = "yyyy-MM-dd'T'HH:mm:sszzz"

type ApiResponse = object
  category: Option[string]
  date: Option[string]

type
  Shabbat* = object
    date*: DateTime
    shabbat*: DateTime
    havdalah*: DateTime

proc parseDateTime(date: string, timezone: Timezone): DateTime =
  return times.parse(date, formatString, timezone)

proc formatTime(s: Shabbat): string =
  let timeLeft: DurationParts = (s.shabbat - s.date).toParts()
  let hours = timeLeft[Hours]
  let minutes = timeLeft[Minutes]
  var ending = minutes
  result = "через"

  if hours != 0:
    var hour_string = "час";
    if (hours >= 2 and hours < 5) or (hours >= 22 and hours < 25):
      hour_string.add("а")
    elif hours >= 5 and hours < 21:
      hour_string.add("ов")
    result.addf(" $1 $2", hours, hour_string)
  if minutes != 0:
    result.addf(" $1 минут", minutes)

  if hours == 0 and minutes == 0:
    let seconds = timeLeft[Seconds]
    result.addf(" $1 секунд", seconds)
    ending = seconds

  let lastDigit = ending mod 10
  if lastDigit == 1:
    result.add("у")
  elif (ending > 21 or ending < 5) and lastDigit >= 2 and lastDigit < 5:
    result.add("ы")

  return result

proc calculateTime*(s: Shabbat): string =
  if s.date < s.shabbat:
    return s.formatTime()
  elif s.date < s.havdalah:
    return "ого, шаббат ебать"
  return "бля, шаббат кончился"

proc fromJson*(json: JsonNode): Shabbat {.gcsafe.} =
  let jerusalem = tz"Asia/Jerusalem"
  let response = to(json, seq[ApiResponse])
  let epoch = parse("1970-01-01", "yyyy-MM-dd")
  var shabbat: DateTime = epoch
  var havdalah: DateTime = epoch
  for item in response:
    if item.category.isSome() and item.date.isSome():
      case item.category.get():
      of "candles":
        shabbat = parseDateTime(item.date.get(), jerusalem)
      of "havdalah":
        havdalah = parseDateTime(item.date.get(), jerusalem)
      else: discard
  let currentDate = now().inZone(jerusalem)
  return Shabbat(date: currentDate, shabbat: shabbat, havdalah: havdalah)
