package model;

import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.temporal.ChronoUnit;
import java.util.List;

public class Shabbat {
    private ZonedDateTime shabbatDate;
    private ZonedDateTime havdalahDate;
    private ZonedDateTime date;

    public Shabbat() {}

    public Shabbat(ZonedDateTime date, ZonedDateTime shabbatDate, ZonedDateTime havdalahDate) {
        this.date = date;
        this.shabbatDate = shabbatDate;
        this.havdalahDate = havdalahDate;
    }

    public void setDate(ZonedDateTime date) {
        this.date = date.withZoneSameInstant(ZoneId.of("Asia/Jerusalem"));
    }

    public void setItems(List<Item> items) {
        for (var item : items) {
            var category = item.getCategory();
            if (category == null) continue;
            if (category.equals("candles") && shabbatDate == null) {
                shabbatDate = item.getDate();
            } else if (category.equals("havdalah") && havdalahDate == null) {
                havdalahDate = item.getDate();
            }
        }
    }

    public String calculateTime() {
        if (date.isBefore(shabbatDate)) {
            var days = date.until(shabbatDate, ChronoUnit.DAYS);
            if (days > 0) {
                return "после".repeat((int)days-1) + "завтра";
            } else {
                return Util.formatDuration(date, shabbatDate);
            }
        } else if (date.isBefore(havdalahDate)) {
            return "ого, шаббат ебать";
        }
        return "бля, шаббат кончился";
    }
}
