package com.rww.wetypeswipe;

final class ParagraphNavigator {
    private ParagraphNavigator() {}

    static int distanceToStart(CharSequence before) {
        if (before == null) return 0;
        for (int index = before.length() - 1; index >= 0; index--) {
            if (isLineBreak(before.charAt(index))) return before.length() - index - 1;
        }
        return before.length();
    }

    static int distanceToEnd(CharSequence after) {
        if (after == null) return 0;
        for (int index = 0; index < after.length(); index++) {
            if (isLineBreak(after.charAt(index))) return index;
        }
        return after.length();
    }

    static int clampIndex(int value, int length) {
        if (value < 0) return 0;
        return Math.min(value, Math.max(0, length));
    }

    private static boolean isLineBreak(char value) {
        return value == '\n' || value == '\r' || value == '\u2028' || value == '\u2029';
    }
}
