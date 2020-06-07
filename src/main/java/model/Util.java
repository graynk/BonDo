package model;

import com.pengrad.telegrambot.model.Chat;
import com.pengrad.telegrambot.model.Message;

import java.time.ZonedDateTime;
import java.time.temporal.ChronoUnit;
import java.util.Random;

public class Util {
    private final static Random random = new Random();

    public static String formatDuration(ZonedDateTime startDate, ZonedDateTime endDate) {
        var hours = startDate.until(endDate, ChronoUnit.HOURS);
        var minutes = startDate.until(endDate, ChronoUnit.MINUTES) - 60 * hours;
        var result = new StringBuilder("через");
        var ending = minutes;
        if (hours != 0) {
            var hour_string = "час";
            if ((hours >= 2 && hours < 5) || (hours >= 22 && hours < 25))
                hour_string += "а";
            else if (hours >= 5 && hours < 21)
                hour_string += "ов";
            result.append(String.format(" %d %s", hours, hour_string));
        }
        if (minutes != 0) {
            result.append(String.format(" %d минут", minutes));
        }
        if (hours == 0 && minutes == 0) {
            var seconds = startDate.until(endDate, ChronoUnit.SECONDS);
            result.append(String.format(" %d секунд", seconds));
            ending = seconds;
        }
        var lastDigit = ending % 10;
        if (lastDigit == 1) {
            result.append("у");
        } else if ((ending > 21 || ending < 5) && lastDigit >= 2 && lastDigit < 5)
            result.append("ы");
        return result.toString();
    }

    public static String generateOh(String vowel) {
        return vowel.repeat(random.nextInt(8) + 1) +
                "х".repeat(random.nextInt(8) + 1) +
                ".".repeat(random.nextInt(3));
    }

    public static String generateMessageLink(Message message) {
        var chat = message.chat();
        if (chat.type() == Chat.Type.group || chat.type() == Chat.Type.Private) {
            return "";
        }
        String chatLink;
        if (chat.username() != null) {
            chatLink = chat.username();
        } else {
            chatLink = "c/" + chat.id().toString().substring(4);
        }
        return String.format("https://t.me/%s/%d", chatLink, message.messageId());
    }
}
