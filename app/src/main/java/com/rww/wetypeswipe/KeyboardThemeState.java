package com.rww.wetypeswipe;

import android.content.res.Configuration;

final class KeyboardThemeState {
    private KeyboardThemeState() {}

    static int resolveNightMode(int keyboardUiMode, int applicationUiMode, int imeUiMode) {
        int application = nightBits(applicationUiMode);
        if (isDefined(application)) return application;

        int ime = nightBits(imeUiMode);
        if (isDefined(ime)) return ime;

        int keyboard = nightBits(keyboardUiMode);
        return isDefined(keyboard) ? keyboard : Configuration.UI_MODE_NIGHT_UNDEFINED;
    }

    static boolean isNight(int nightMode) {
        return nightBits(nightMode) == Configuration.UI_MODE_NIGHT_YES;
    }

    static long paintSignature(int width, int height, int keyHeight, int densityBits, int nightMode) {
        return (((long) width) << 40)
                ^ (((long) height) << 16)
                ^ (((long) keyHeight) << 4)
                ^ (((long) nightBits(nightMode)) << 2)
                ^ (densityBits & 0xffffffffL);
    }

    private static int nightBits(int uiMode) {
        return uiMode & Configuration.UI_MODE_NIGHT_MASK;
    }

    private static boolean isDefined(int nightMode) {
        return nightMode == Configuration.UI_MODE_NIGHT_NO
                || nightMode == Configuration.UI_MODE_NIGHT_YES;
    }
}
