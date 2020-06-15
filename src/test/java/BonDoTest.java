import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class BonDoTest {

    @Test
    void handleBaguette() {
        assertTrue(BonDo.baguettePattern.matcher("хохохо").find());
        assertTrue(BonDo.baguettePattern.matcher("хохохохо").find());
        assertFalse(BonDo.baguettePattern.matcher("хохо").find());
        assertFalse(BonDo.baguettePattern.matcher("хохохохохо").find());
        assertFalse(BonDo.baguettePattern.matcher("охохо").find());

        assertTrue(BonDo.baguettePattern.matcher("мммм багет багет багет!").find());
        assertTrue(BonDo.baguettePattern.matcher("багеть").find());
        assertFalse(BonDo.baguettePattern.matcher("багетъ").find());
        assertFalse(BonDo.baguettePattern.matcher("багетованный").find());
    }
}