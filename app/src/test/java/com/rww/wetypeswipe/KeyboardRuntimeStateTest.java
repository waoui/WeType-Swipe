package com.rww.wetypeswipe;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public class KeyboardRuntimeStateTest {
    @Test public void classifiesQwertyOnce() {
        KeyboardRuntimeState state = KeyboardRuntimeState.classify(
                "com.tencent.wetype.keyboard.QwertyKeyboard", false);
        assertEquals(KeyboardRuntimeState.Mode.QWERTY, state.mode);
        assertFalse(state.handwriting);
    }

    @Test public void classifiesT9Once() {
        KeyboardRuntimeState state = KeyboardRuntimeState.classify(
                "com.tencent.wetype.keyboard.T9Keyboard", false);
        assertEquals(KeyboardRuntimeState.Mode.T9, state.mode);
    }

    @Test public void handwritingOverridesKeyboardName() {
        KeyboardRuntimeState state = KeyboardRuntimeState.classify(
                "com.tencent.wetype.keyboard.QwertyKeyboard", true);
        assertEquals(KeyboardRuntimeState.Mode.HANDWRITING, state.mode);
        assertTrue(state.handwriting);
    }

    @Test public void unknownKeyboardIsOther() {
        assertEquals(KeyboardRuntimeState.Mode.OTHER,
                KeyboardRuntimeState.classify("x.y.CustomKeyboard", false).mode);
    }
}
