package com.rww.wetypeswipe;

import static org.junit.Assert.assertEquals;
import org.junit.Test;

public final class GestureDirectionTest {
    @Test public void downwardOnlyMatchesPositiveY() {
        assertEquals(1, GestureDirection.resolve(0, 13, 12, false, true, false));
        assertEquals(0, GestureDirection.resolve(0, -13, 12, false, true, false));
    }
    @Test public void upwardOnlyMatchesNegativeY() {
        assertEquals(-1, GestureDirection.resolve(0, -13, 12, false, false, true));
        assertEquals(0, GestureDirection.resolve(0, 13, 12, false, false, true));
    }
    @Test public void twoDirectionsAreDistinctAndDoNotFireBeforeThreshold() {
        assertEquals(0, GestureDirection.resolve(0, -11.9f, 12, false, true, true));
        assertEquals(1, GestureDirection.resolve(0, 12, 12, false, true, true));
        assertEquals(-1, GestureDirection.resolve(0, -12, 12, false, true, true));
    }
    @Test public void horizontalTypingDoesNotTriggerEitherDirection() {
        assertEquals(0, GestureDirection.resolve(90, -20, 12, false, true, true));
        assertEquals(0, GestureDirection.resolve(90, 20, 12, false, true, true));
        assertEquals(0, GestureDirection.resolve(30, -20, 20, true, true, true));
        assertEquals(-1, GestureDirection.resolve(3, -21, 20, true, true, true));
    }
}
