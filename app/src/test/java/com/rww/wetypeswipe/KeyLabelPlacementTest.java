package com.rww.wetypeswipe;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import org.junit.Test;

public final class KeyLabelPlacementTest {
    @Test public void upperTextIsAboveKeyCenterAndLowerTextBelowCenter() {
        float top = 100f, bottom = 150f, padding = 2f;
        float ascent = -9f, descent = 2f;
        float up = KeyLabelPlacement.upBaseline(top, padding, ascent);
        float down = KeyLabelPlacement.downBaseline(bottom, padding, descent);
        assertEquals(111f, up, 0.001f);
        assertEquals(146f, down, 0.001f);
        assertTrue(up < (top + bottom) / 2f);
        assertTrue(down > (top + bottom) / 2f);
        assertTrue(up + ascent >= top);
        assertTrue(down + descent <= bottom);
    }

    @Test public void positionIsRelativeToCurrentRowNotWholeKeyboard() {
        float rowHeight = 50f, padding = 2f, ascent = -9f, descent = 2f;
        for (int row = 0; row < 3; row++) {
            float top = row * rowHeight;
            float bottom = top + rowHeight;
            float up = KeyLabelPlacement.upBaseline(top, padding, ascent);
            float down = KeyLabelPlacement.downBaseline(bottom, padding, descent);
            assertTrue(up > top && up < top + rowHeight * .4f);
            assertTrue(down > top + rowHeight * .6f && down < bottom);
        }
    }
}
