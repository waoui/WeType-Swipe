package com.rww.wetypeswipe;

import java.util.Arrays;

final class EmbeddedConfigEditor {
    static final int[] QWERTY_ACTIONS = ActionRegistry.qwertyActions();

    private EmbeddedConfigEditor() {}

    static int actionForQwerty(Config config, String key) {
        if (config == null || key == null || key.length() != 1) return Config.ACTION_NONE;
        int index = key.charAt(0) - 'a';
        if (index >= 0 && index < config.qwertyTexts.length
                && !Config.normalizeInsertedText(config.qwertyTexts[index]).isEmpty()) return Config.ACTION_INSERT_TEXT;
        if (config.disabledKeys != null && config.disabledKeys.contains(key)) return Config.ACTION_DISABLE;
        for (int action : QWERTY_ACTIONS) {
            if (key.equals(keyForAction(config, action))) return action;
        }
        return Config.ACTION_NONE;
    }

    static void assignQwerty(Config config, String key, int action) {
        if (config == null || key == null || key.length() != 1) return;
        for (int existing : QWERTY_ACTIONS) {
            if (key.equals(keyForAction(config, existing))) setKeyForAction(config, existing, "");
        }
        int keyIndex = key.charAt(0) - 'a';
        if (keyIndex >= 0 && keyIndex < config.qwertyTexts.length) config.qwertyTexts[keyIndex] = "";
        config.disabledKeys = removeKey(config.disabledKeys, key);
        if (action == Config.ACTION_INSERT_TEXT) {
            // Text is assigned by assignQwertyText after the editor dialog returns.
        } else if (action == Config.ACTION_DISABLE) {
            config.disabledKeys = normalizeKeys((config.disabledKeys == null ? "" : config.disabledKeys) + key);
        } else if (action != Config.ACTION_NONE) {
            setKeyForAction(config, action, key);
        }
        config.rebuildActionMap();
    }

    static void assignQwertyText(Config config, String key, String text) {
        assignQwerty(config, key, Config.ACTION_NONE);
        if (config == null || key == null || key.length() != 1) return;
        int index = key.charAt(0) - 'a';
        if (index < 0 || index >= config.qwertyTexts.length) return;
        config.qwertyTexts[index] = Config.normalizeInsertedText(text);
        config.rebuildActionMap();
    }

    static void assignT9Text(Config config, int digit, String text) {
        if (config == null || digit < 2 || digit > 9) return;
        config.t9Actions[digit] = Config.ACTION_INSERT_TEXT;
        config.t9Texts[digit] = Config.normalizeInsertedText(text);
        config.rebuildActionMap();
    }

    static void clearT9Text(Config config, int digit) {
        if (config == null || digit < 2 || digit > 9) return;
        config.t9Texts[digit] = "";
    }

    static void restoreDefaults(Config config) {
        if (config == null) return;
        for (int action : QWERTY_ACTIONS) setKeyForAction(config, action, "");
        config.selectAll = "z";
        config.cut = "x";
        config.copy = "c";
        config.paste = "v";
        config.disabledKeys = "";
        Arrays.fill(config.qwertyTexts, "");
        config.rebuildActionMap();
    }

    static void clearQwerty(Config config) {
        if (config == null) return;
        for (int action : QWERTY_ACTIONS) setKeyForAction(config, action, "");
        config.disabledKeys = "";
        Arrays.fill(config.qwertyTexts, "");
        config.rebuildActionMap();
    }

    static String keyForAction(Config config, int action) {
        return ActionRegistry.keyFor(config, action);
    }

    static void setKeyForAction(Config config, int action, String key) {
        ActionRegistry.setKey(config, action, key);
    }

    private static String removeKey(String keys, String key) {
        return keys == null ? "" : keys.replace(key, "");
    }

    private static String normalizeKeys(String value) {
        boolean[] seen = new boolean[26];
        StringBuilder out = new StringBuilder();
        if (value == null) return "";
        for (int i = 0; i < value.length(); i++) {
            char c = Character.toLowerCase(value.charAt(i));
            if (c < 'a' || c > 'z' || seen[c - 'a']) continue;
            seen[c - 'a'] = true;
            out.append(c);
        }
        return out.toString();
    }
}
