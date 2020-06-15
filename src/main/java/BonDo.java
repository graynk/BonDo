import com.fasterxml.jackson.databind.ObjectMapper;
import com.github.kilianB.matcher.persistent.database.H2DatabaseImageMatcher;
import com.pengrad.telegrambot.TelegramBot;
import com.pengrad.telegrambot.UpdatesListener;
import com.pengrad.telegrambot.model.Chat;
import com.pengrad.telegrambot.model.PhotoSize;
import com.pengrad.telegrambot.model.Update;
import com.pengrad.telegrambot.request.GetFile;
import com.pengrad.telegrambot.request.SendMessage;
import com.pengrad.telegrambot.request.SendSticker;
import com.pengrad.telegrambot.request.SendVideoNote;
import com.pengrad.telegrambot.request.SendVoice;
import model.Shabbat;
import model.Util;

import javax.imageio.ImageIO;
import java.io.IOException;
import java.net.URI;
import java.net.URL;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.sql.SQLException;
import java.time.DayOfWeek;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.temporal.TemporalAdjusters;
import java.util.List;
import java.util.regex.Pattern;

import static model.Util.generateOh;

public class BonDo implements UpdatesListener {
    private final TelegramBot bot;
    private final ObjectMapper mapper;
    private final H2DatabaseImageMatcher imageMatcher;
    final static Pattern ohPattern = Pattern.compile(
            "(\\b[oо]+|\\b[аa]+|\\b[ы]+|\\b[еe]+|\\b[уy]+|\\b[э]+)[xх]+\\b",
            Pattern.CASE_INSENSITIVE | Pattern.UNICODE_CASE
    );
    final static Pattern baguettePattern = Pattern.compile(
            "(\\b((хо){3,4}|багет[ь]?)\\b)",
            Pattern.CASE_INSENSITIVE | Pattern.UNICODE_CASE
    );
    final static Pattern foolPattern = Pattern.compile(
            "(\\b[ё]+|\\b[ю]+|\\b[я]+)[xх]+\\b",
            Pattern.CASE_INSENSITIVE | Pattern.UNICODE_CASE
    );
    private final URI shabbatURI = URI.create("https://www.hebcal.com/shabbat/?cfg=json&geo=Jerusalem&geonameid=281184");
    private final ZoneId jerusalem = ZoneId.of("Asia/Jerusalem");

    public BonDo(String token, ObjectMapper mapper, H2DatabaseImageMatcher imageMatcher) throws IOException {
        this.bot = new TelegramBot(token);
        this.mapper = mapper;
        this.imageMatcher = imageMatcher;
    }

    public void start() {
        bot.setUpdatesListener(this);
    }

    @Override
    public int process(List<Update> updates) {
        for (var update : updates) {
            if (update.message() == null) {
                continue;
            }
            var message = update.message();
            var chatId = message.chat().id();
            if (message.text() != null) {
                var text = message.text();
                var handled = false;
                handled = handleOh(chatId, text);
                if (!handled)
                    handled = handleShabbat(chatId, text);
                if (!handled)
                    handled = handleShabaka(chatId, text);
                if (!handled) {
                    handleBaguette(chatId, text);
                }
            } else if (message.photo() != null && message.photo().length > 0 && message.chat().type() == Chat.Type.supergroup) {
                var link = Util.generateMessageLink(message);
                handlePhoto(chatId, message.messageId(), link, message.photo());
            } else if (message.poll() != null) {
                handleUkranianPolls(chatId, message.forwardFromChat());
            }
        }
        return UpdatesListener.CONFIRMED_UPDATES_ALL;
    }

    private boolean handleOh(Long chatId, String text) {
        var matcher = ohPattern.matcher(text);
        if (matcher.find()) {
            var oh = generateOh(matcher.group(0).substring(0, 1).toLowerCase());
            bot.execute(new SendMessage(chatId, oh));
            return true;
        } else if (foolPattern.matcher(text).find()) {
            bot.execute(new SendMessage(chatId, "ну ты дурак штоле?"));
            return true;
        }
        return false;
    }

    private boolean handleShabbat(Long chatId, String text) {
        if (!text.toLowerCase().contains("когда шаббат")) {
            return false;
        }
        try {
            var now = ZonedDateTime.now(jerusalem);
            Shabbat shabbat;
            if (now.getDayOfWeek() == DayOfWeek.FRIDAY) {
                var request = HttpRequest.newBuilder(shabbatURI)
                        .header("Accept", "application/json")
                        .GET()
                        .build();
                var client = HttpClient.newHttpClient();
                var response = client.send(request, HttpResponse.BodyHandlers.ofString());
                shabbat = mapper.readValue(response.body(), Shabbat.class);
            } else {
                var nextFriday = now.with(TemporalAdjusters.next(DayOfWeek.FRIDAY));
                shabbat = new Shabbat(now, nextFriday, nextFriday.plusDays(1));
            }
            bot.execute(new SendMessage(chatId, shabbat.calculateTime()));
        } catch (InterruptedException | IOException e) {
            e.printStackTrace();
        }
        return true;
    }

    private boolean handleShabaka(Long chatId, String text) {
        if (!text.toLowerCase().contains("когда шабака")) {
            return false;
        }
        // гау гау
        bot.execute(new SendSticker(chatId, "CAACAgIAAx0CRIwq1wACB_1e3MxXXPUDini1VgABFkMm1eMtl_MAAlYAA0lgaApie_5XONzdohoE"));
        return true;
    }

    private void handleUkranianPolls(Long chatId, Chat forwardFrom) {
        if (forwardFrom == null) {
            return;
        }
        if (forwardFrom.id() != -1001404061676L) {
            return;
        }
        bot.execute(new SendVoice(chatId, "AwACAgIAAx0CRIwq1wACCF9e56cGg6_B4h9zUsNyfpKRg34s4gACOQcAAh4VOEs435hLXOjWFRoE"));
    }

    private void handleBaguette(Long chatId, String text) {
        var matcher = baguettePattern.matcher(text);
        if (matcher.find()) {
            bot.execute(new SendVideoNote(chatId, "DQACAgIAAx0CRIwq1wACCFZe56arCYZRPfOAOHvgi243TH4URAACOAcAAh4VOEvw1eDWrZFm-BoE"));
        }
    }

    private void handlePhoto(Long chatId, Integer replyId, String link, PhotoSize[] photoSizes) {
        var biggestPhoto = photoSizes[0];
        for (var photo : photoSizes) {
            if (photo.width() > biggestPhoto.width()) {
                biggestPhoto = photo;
            }
        }
        var getFile = new GetFile(biggestPhoto.fileId());
        var fileResponse = bot.execute(getFile);
        var downloadPath = bot.getFullFilePath(fileResponse.file());
        try {
            var url = new URL(downloadPath);
            var image = ImageIO.read(url.openStream());
            var matched = imageMatcher.getMatchingImages(image, chatId);
            if (matched.size() > 0) {
                var result = matched.poll();
                bot.execute(new SendMessage(chatId, "дед, таблетки\n" + result.value).replyToMessageId(replyId));
            } else {
                imageMatcher.addImage(link, image, chatId);
            }
        } catch (IOException | SQLException e) {
            e.printStackTrace();
        }
    }
}
