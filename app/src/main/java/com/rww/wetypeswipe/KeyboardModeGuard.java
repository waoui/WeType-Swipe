package com.rww.wetypeswipe;

import java.util.Locale;

final class KeyboardModeGuard {
    private KeyboardModeGuard() {}

    static boolean isHandwritingClassName(String className) {
        if (className == null || className.isEmpty()) return false;
        String normalized = className.toLowerCase(Locale.ROOT);
        return normalized.contains("handwrite") || normalized.contains("hand_write");
    }
}
