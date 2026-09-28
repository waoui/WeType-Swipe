package com.rww.wetypeswipe;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public class KeyboardRuntimeStateTest {
    @Test public void classNameClassificationIsCachedOnce() {
        KeyboardRuntimeState qwerty = new KeyboardRuntimeState("demo.QwertyPinyinKeyboard");
        assertTrue(qwerty.qwertyClass);
        assertFalse(qwerty.t9Class);

        KeyboardRuntimeState t9 = new KeyboardRuntimeState("demo.NineT9Keyboard");
        assertTrue(t9.t9Class);
        assertFalse(t9.qwertyClass);
    }

    @Test public void handwritingRefreshIsThrottledButCanBeForced() {
        KeyboardRuntimeState state = new KeyboardRuntimeState("demo.QwertyKeyboard");
        assertTrue(state.shouldRefreshHandwriting(1000L, false));

        state.updateHandwriting(true, 1000L);
        assertTrue(state.handwriting());
        assertFalse(state.shouldRefreshHandwriting(1100L, false));
        assertTrue(state.shouldRefreshHandwriting(
                1000L + KeyboardRuntimeState.HANDWRITING_REFRESH_MS, false));
        assertTrue(state.shouldRefreshHandwriting(1100L, true));
    }
}
