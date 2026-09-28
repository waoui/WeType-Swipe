package com.rww.wetypeswipe;

import android.view.MotionEvent;

import java.util.Locale;

/** Resolves WeType's obfuscated key models into stable QWERTY/T9 identities. */
final class KeyResolver {
    private final Reflector reflector;

    KeyResolver(Reflector reflector) {
        this.reflector = reflector;
    }

    KeyInfo keyAfterDown(Object keyboard, MotionEvent event) {
        Object button = reflector.invoke(keyboard, "getActionButton");
        if (button == null) button = reflector.invoke(keyboard, "v1", event, false);
        if (button == null) button = reflector.invoke(keyboard, "v1", event, true);
        return keyFromButton(keyboard, button);
    }

    KeyInfo visibleKeyFromButton(Object button) {
        if (button == null) return null;
        Object keyData = reflector.invoke(button, "O");
        if (keyData == null) return null;
        Object main = reflector.invoke(keyData, "getMainText");
        Object secondary = secondaryText(keyData);
        return keyFromTexts(main, secondary);
    }

    KeyInfo keyFromButton(Object keyboard, Object button) {
        if (button == null) return null;
        Object keyData = reflector.invoke(button, "O");
        if (keyData != null) {
            Object main = reflector.invoke(keyData, "getMainText");
            Object secondary = secondaryText(keyData);
            KeyInfo key = keyFromTexts(main, secondary);
            if (key != null) return key;
            if (isT9Context(keyboard, button, keyData)) {
                String numeric = numericT9Key(main);
                if (numeric != null) return KeyInfo.t9(numeric);
            }
            key = keyFromId(reflector.invoke(keyData, "getId"), keyboard, button, keyData);
            if (key != null) return key;
        }
        return keyFromId(reflector.invoke(button, "K"), keyboard, button, keyData);
    }

    private Object secondaryText(Object keyData) {
        Object value = reflector.invoke(keyData, "getSubText");
        if (value != null) return value;
        value = reflector.invoke(keyData, "getSecondaryText");
        if (value != null) return value;
        value = reflector.invoke(keyData, "getHintText");
        if (value != null) return value;
        return reflector.invoke(keyData, "getAssistText");
    }

    static KeyInfo keyFromTexts(Object mainValue, Object secondaryValue) {
        String main = normalizeText(mainValue);
        String secondary = normalizeText(secondaryValue);
        String digit = t9DigitFromLetters(main + secondary);
        if (digit != null) return KeyInfo.t9(digit);
        if (main.length() == 1) {
            char c = main.charAt(0);
            if (c >= 'a' && c <= 'z') return KeyInfo.alpha(String.valueOf(c));
        }
        return null;
    }

    private static String normalizeText(Object value) {
        if (value == null) return "";
        String text = String.valueOf(value).trim().toLowerCase(Locale.ROOT);
        StringBuilder clean = null;
        for (int index = 0; index < text.length(); index++) {
            char c = text.charAt(index);
            boolean allowed = (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9');
            if (allowed) {
                if (clean != null) clean.append(c);
            } else if (clean == null) {
                clean = new StringBuilder(text.length());
                clean.append(text, 0, index);
            }
        }
        return clean == null ? text : clean.toString();
    }

    private static String numericT9Key(Object value) {
        String text = normalizeText(value);
        if (text.length() == 1) {
            char c = text.charAt(0);
            if (c >= '2' && c <= '9') return String.valueOf(c);
        }
        return null;
    }

    private static String t9DigitFromLetters(String value) {
        if (value == null || value.isEmpty()) return null;
        if (lettersMatch(value, "abc")) return "2";
        if (lettersMatch(value, "def")) return "3";
        if (lettersMatch(value, "ghi")) return "4";
        if (lettersMatch(value, "jkl")) return "5";
        if (lettersMatch(value, "mno")) return "6";
        if (lettersMatch(value, "pqrs")) return "7";
        if (lettersMatch(value, "tuv")) return "8";
        if (lettersMatch(value, "wxyz")) return "9";
        return null;
    }

    private static boolean lettersMatch(String value, String expected) {
        int matched = 0;
        for (int index = 0; index < value.length(); index++) {
            char c = value.charAt(index);
            if (c < 'a' || c > 'z') continue;
            if (matched >= expected.length() || c != expected.charAt(matched)) return false;
            matched++;
        }
        return matched == expected.length();
    }

    private static KeyInfo keyFromId(Object value, Object keyboard, Object button, Object keyData) {
        if (value == null) return null;
        String text = String.valueOf(value).trim().toLowerCase(Locale.ROOT);
        int index = text.lastIndexOf("_key_");
        String tail = index >= 0 ? text.substring(index + 5) : text;
        if (tail.length() == 1) {
            char c = tail.charAt(0);
            if (c >= 'a' && c <= 'z') return KeyInfo.alpha(String.valueOf(c));
        }
        if (!tail.isEmpty()) {
            char last = tail.charAt(tail.length() - 1);
            if (last >= 'a' && last <= 'z'
                    && (tail.endsWith("_" + last) || tail.endsWith("key" + last))) {
                return KeyInfo.alpha(String.valueOf(last));
            }
        }
        boolean t9Hint = text.contains("t9") || text.contains("nine")
                || isT9Context(keyboard, button, keyData);
        if (t9Hint) {
            for (int i = text.length() - 1; i >= 0; i--) {
                char c = text.charAt(i);
                if (c >= '2' && c <= '9') return KeyInfo.t9(String.valueOf(c));
            }
        }
        return null;
    }

    private static boolean isT9Context(Object... values) {
        for (Object value : values) {
            String name = value == null ? "" : value.getClass().getName().toLowerCase(Locale.ROOT);
            if (name.contains("t9") || name.contains("nine")) return true;
        }
        return false;
    }
}
