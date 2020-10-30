import json
import shabbat
import httpclient
import telebot, asyncdispatch, logging, options
import regex
import strutils
import times
import unicode
import utils
import os

var L = newConsoleLogger(fmtStr="$levelname, [$time] ")
addHandler(L)

const API_KEY = getEnv("BONDO_TOKEN")
const OH_PATTERN = re(r"(?i)(\b[oо]+|\b[аa]+|\b[ы]+|\b[еe]+|\b[уy]+|\b[э]+)[xх]+\b")
const BAGUETTE_PATTERN = re(r"(?i)(\b((хо){3,4}|багет((ь)?|(а)?|(ом)?|(ов)?|(ы)?))\b)")
const FOOL_PATTERN = re(r"(?i)(\b[ё]+|\b[ю]+|\b[я]+)[xх]+\b")
const BAGUETTE_PATH = "file://./baguette.mp4"

proc updateHandler(b: Telebot, u: Update): Future[bool] {.async.} =
  if not u.message.isSome:
    return true
  var response = u.message.get
  if response.text.isSome:
    let text = response.text.get
    var m: RegexMatch
    if text.contains(FOOL_PATTERN):
      discard await b.sendMessage(response.chat.id, "ну ты дурак штоле?")
    elif text.contains(BAGUETTE_PATTERN):
      discard await b.sendVideoNote(response.chat.id, BAGUETTE_PATH)
    elif text.toLower().contains("когда шабака"):
      discard await b.sendSticker(response.chat.id, "CAACAgIAAx0CRIwq1wACB_1e3MxXXPUDini1VgABFkMm1eMtl_MAAlYAA0lgaApie_5XONzdohoE")
    elif text.toLower().contains("когда шаббат"):
      let currentWeekday = now().weekday
      let daysLeft = ord(dFri) - ord(currentWeekday)
      var message: string
      if daysLeft > 0:
        message = "после".repeat(daysLeft-1) & "завтра"
      elif currentWeekday == dSun:
        message = "после".repeat(ord(high(WeekDay)) + daysLeft) & "завтра"
      else:
        let client = newHttpClient()
        let content = client.getContent("https://www.hebcal.com/shabbat/?cfg=json&geo=Jerusalem&geonameid=281184")
        let jsonNode = parseJson(content)
        let shabbat = fromJson(jsonNode["items"])
        message = shabbat.calculateTime()
      discard await b.sendMessage(response.chat.id, message)
    elif text.find(OH_PATTERN, m):
      let vowel = m.groupFirstCapture(0, text)
      discard await b.sendMessage(response.chat.id, generateOh(vowel))

let bot = newTeleBot(API_KEY)
bot.onUpdate(updateHandler)
bot.poll(timeout=300)