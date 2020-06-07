package model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;

import java.time.ZonedDateTime;

@JsonIgnoreProperties(value = { "link", "title", "hebrew", "category", "leyning" })
public class Item {
    @JsonDeserialize(using = ZonedDateTimeDeserializer.class)
    private ZonedDateTime date;

    public ZonedDateTime getDate() {
        return date;
    }

    public void setDate(ZonedDateTime date) {
        this.date = date;
    }
}
