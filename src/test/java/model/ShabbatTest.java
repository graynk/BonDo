package model;

import org.junit.jupiter.api.Test;

import java.time.ZoneId;
import java.time.ZonedDateTime;

import static org.junit.jupiter.api.Assertions.*;

class ShabbatTest {

    @Test
    void calculateTime() {
        var current = ZonedDateTime.of(
                2020,
                6,
                1,
                0,
                2,
                0,
                0,
                ZoneId.of("Asia/Jerusalem")
        );
        var shabbat = ZonedDateTime.of(
                2020,
                6,
                5,
                19,
                2,
                0,
                0,
                ZoneId.of("Asia/Jerusalem")
        );
        var havdalah = ZonedDateTime.of(
                2020,
                6,
                6,
                20,
                32,
                0,
                0,
                ZoneId.of("Asia/Jerusalem")
        );

        var calculator = new Shabbat(current, shabbat, havdalah);
        assertEquals("послепослепослезавтра", calculator.calculateTime());
        calculator.setDate(current.plusDays(1));
        assertEquals("послепослезавтра", calculator.calculateTime());
        calculator.setDate(current.plusDays(2));
        assertEquals("послезавтра", calculator.calculateTime());
        calculator.setDate(current.plusDays(3));
        assertEquals("завтра", calculator.calculateTime());
        current = current.plusDays(4);
        calculator.setDate(current);
        assertEquals("через 19 часов", calculator.calculateTime());
        current = current.plusMinutes(1);
        calculator.setDate(current);
        assertEquals("через 18 часов 59 минут", calculator.calculateTime());
        current = current.plusMinutes(5);
        calculator.setDate(current);
        assertEquals("через 18 часов 54 минуты", calculator.calculateTime());
        current = current.plusMinutes(3);
        calculator.setDate(current);
        assertEquals("через 18 часов 51 минуту", calculator.calculateTime());
        current = current.plusMinutes(1);
        calculator.setDate(current);
        assertEquals("через 18 часов 50 минут", calculator.calculateTime());
        current = current.plusHours(18);
        calculator.setDate(current);
        assertEquals("через 50 минут", calculator.calculateTime());
        current = current.plusMinutes(38);
        calculator.setDate(current);
        assertEquals("через 12 минут", calculator.calculateTime());
        current = current.plusMinutes(8);
        calculator.setDate(current);
        assertEquals("через 4 минуты", calculator.calculateTime());
        current = current.plusMinutes(3);
        calculator.setDate(current);
        assertEquals("через 1 минуту", calculator.calculateTime());
        current = current.plusSeconds(1);
        calculator.setDate(current);
        assertEquals("через 59 секунд", calculator.calculateTime());
        current = current.plusSeconds(5);
        calculator.setDate(current);
        assertEquals("через 54 секунды", calculator.calculateTime());
        current = current.plusSeconds(3);
        calculator.setDate(current);
        assertEquals("через 51 секунду", calculator.calculateTime());
        current = current.plusSeconds(51);
        calculator.setDate(current);
        assertEquals("ого, шаббат ебать", calculator.calculateTime());
        current = havdalah.minusSeconds(1);
        calculator.setDate(current);
        assertEquals("ого, шаббат ебать", calculator.calculateTime());
        current = current.plusSeconds(1);
        calculator.setDate(current);
        assertEquals("бля, шаббат кончился", calculator.calculateTime());
        current = current.plusSeconds(1);
        calculator.setDate(current);
        assertEquals("бля, шаббат кончился", calculator.calculateTime());
        current = current.plusDays(1);
        calculator.setDate(current);
        assertEquals("бля, шаббат кончился", calculator.calculateTime());
    }
}