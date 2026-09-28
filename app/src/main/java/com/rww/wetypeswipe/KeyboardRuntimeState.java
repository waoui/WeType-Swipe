package com.rww.wetypeswipe;

import java.util.Locale;

/** Small per-keyboard cache used to keep classification out of touch/draw hot paths. */
final class KeyboardRuntimeState {
    static final long HANDWRITING_REFRESH_MS = 300L;

    final boolean t9Class;
    final boolean qwertyClass;

    private volatile boolean handwriting;
    private volatile long handwritingCheckedAt = Long.MIN_VALUE;

    KeyboardRuntimeState(String className) {
        String name = className == null ? "" : className.toLowerCase(Locale.ROOT);
        t9Class = name.contains("t9") || name.contains("nine");
        qwertyClass = name.contains("qwerty") || name.contains("wubi") || name.contains("pinyin");
    }

    boolean shouldRefreshHandwriting(long now, boolean force) {
        if (force || handwritingCheckedAt == Long.MIN_VALUE) return true;
        long age = now - handwritingCheckedAt;
        return age < 0L || age >= HANDWRITING_REFRESH_MS;
    }

    void updateHandwriting(boolean value, long now) {
        handwriting = value;
        handwritingCheckedAt = now;
    }

    boolean handwriting() {
        return handwriting;
    }
}
