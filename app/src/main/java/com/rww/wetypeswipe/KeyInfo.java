package com.rww.wetypeswipe;

import java.util.Locale;

final class KeyInfo {
    final String key;
    final String display;
    final boolean t9;

    private KeyInfo(String key, String display, boolean t9) {
        this.key = key;
        this.display = display;
        this.t9 = t9;
    }

    static KeyInfo alpha(String key) {
        return new KeyInfo(key, key.toUpperCase(Locale.ROOT), false);
    }

    static KeyInfo t9(String digit) {
        return new KeyInfo(digit, "九宫格 " + Config.t9Label(digit.charAt(0) - '0'), true);
    }
}
