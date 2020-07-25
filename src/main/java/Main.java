
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.json.JsonMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.github.kilianB.hashAlgorithms.PerceptiveHash;
import com.github.kilianB.matcher.persistent.database.H2DatabaseImageMatcher;

import java.io.IOException;
import java.sql.SQLException;

public class Main {
    public static void main(String[] args) throws SQLException, IOException {
        ObjectMapper mapper = JsonMapper.builder()
                .addModule(new JavaTimeModule())
                .build();
        mapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        var db = new H2DatabaseImageMatcher("db/imageHashDB", "user", "");
        db.addHashingAlgorithm(new PerceptiveHash(32), .02);

        var token = System.getenv("BOT_TOKEN");
        var bondo = new BonDo(token, mapper, db);
        bondo.start();
    }
}
