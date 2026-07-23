package com.rww.wetypeswipe;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public final class KeyboardModeGuardTest {
    @Test public void identifiesKnownHandwritingKeyboards() {
        assertTrue(KeyboardModeGuard.isHandwritingClassName(
                "com.tencent.wetype.plugin.hld.keyboard.selfdraw.HandWriteKeyboard"));
        assertTrue(KeyboardModeGuard.isHandwritingClassName(
                "com.tencent.wetype.plugin.hld.keyboard.selfdraw.HandWriteFullScreenKeyboard"));
        assertTrue(KeyboardModeGuard.isHandwritingClassName(
                "com.tencent.wetype.plugin.hld.keyboard.selfdraw.S27HandwriteT9Keyboard"));
        assertTrue(KeyboardModeGuard.isHandwritingClassName(
                "com.tencent.wetype.plugin.hld.keyboard.selfdraw.S28HandwriteT26Keyboard"));
        assertTrue(KeyboardModeGuard.isHandwritingClassName(
                "com.tencent.wetype.plugin.hld.handwrite.ImeHandWriteKeyboardView"));
    }

    @Test public void keepsNormalKeyboardsEnabled() {
        assertFalse(KeyboardModeGuard.isHandwritingClassName(null));
        assertFalse(KeyboardModeGuard.isHandwritingClassName(""));
        assertFalse(KeyboardModeGuard.isHandwritingClassName(
                "com.tencent.wetype.plugin.hld.keyboard.selfdraw.QwertyKeyboard"));
        assertFalse(KeyboardModeGuard.isHandwritingClassName(
                "com.tencent.wetype.plugin.hld.keyboard.selfdraw.S27T9Keyboard"));
    }
}
