package com.rww.wetypeswipe;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotEquals;
import static org.junit.Assert.assertTrue;

import android.content.res.Configuration;

import org.junit.Test;

public class KeyboardThemeStateTest {
    @Test public void applicationModeOverridesStaleKeyboardMode() {
        assertEquals(Configuration.UI_MODE_NIGHT_NO,
                KeyboardThemeState.resolveNightMode(
                        Configuration.UI_MODE_NIGHT_YES,
                        Configuration.UI_MODE_NIGHT_NO,
                        Configuration.UI_MODE_NIGHT_YES));
        assertEquals(Configuration.UI_MODE_NIGHT_YES,
                KeyboardThemeState.resolveNightMode(
                        Configuration.UI_MODE_NIGHT_NO,
                        Configuration.UI_MODE_NIGHT_YES,
                        Configuration.UI_MODE_NIGHT_NO));
    }

    @Test public void imeModeIsFallbackWhenApplicationModeUndefined() {
        assertEquals(Configuration.UI_MODE_NIGHT_YES,
                KeyboardThemeState.resolveNightMode(
                        Configuration.UI_MODE_NIGHT_NO,
                        Configuration.UI_MODE_NIGHT_UNDEFINED,
                        Configuration.UI_MODE_NIGHT_YES));
    }

    @Test public void keyboardModeIsLastFallback() {
        assertEquals(Configuration.UI_MODE_NIGHT_NO,
                KeyboardThemeState.resolveNightMode(
                        Configuration.UI_MODE_NIGHT_NO,
                        Configuration.UI_MODE_NIGHT_UNDEFINED,
                        Configuration.UI_MODE_NIGHT_UNDEFINED));
    }

    @Test public void sameKeyboardGetsNewPaintSignatureWhenLiveThemeChanges() {
        int density = Float.floatToIntBits(3.0f);
        long light = KeyboardThemeState.paintSignature(
                1080, 720, 144, density, Configuration.UI_MODE_NIGHT_NO);
        long dark = KeyboardThemeState.paintSignature(
                1080, 720, 144, density, Configuration.UI_MODE_NIGHT_YES);
        assertNotEquals(light, dark);
        assertTrue(KeyboardThemeState.isNight(Configuration.UI_MODE_NIGHT_YES));
    }
}
