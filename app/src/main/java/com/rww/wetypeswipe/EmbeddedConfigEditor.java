package com.rww.wetypeswipe;

final class EmbeddedConfigEditor {
    static final int[] QWERTY_ACTIONS = {
            Config.ACTION_SELECT_ALL,
            Config.ACTION_CUT,
            Config.ACTION_COPY,
            Config.ACTION_PASTE,
            Config.ACTION_COPY_ALL,
            Config.ACTION_CUT_ALL,
            Config.ACTION_PARAGRAPH_START,
            Config.ACTION_PARAGRAPH_END,
            Config.ACTION_SELECT_TO_PARAGRAPH_START,
            Config.ACTION_SELECT_TO_PARAGRAPH_END,
            Config.ACTION_OPEN_CLIPBOARD,
            Config.ACTION_OPEN_QUICK_PHRASE,
            Config.ACTION_UNDO,
            Config.ACTION_REDO,
            Config.ACTION_DOCUMENT_START,
            Config.ACTION_DOCUMENT_END,
            Config.ACTION_SELECT_TO_DOCUMENT_START,
            Config.ACTION_SELECT_TO_DOCUMENT_END
    };

    private EmbeddedConfigEditor() {}

    static int actionForQwerty(Config config, String key) {
        if (config == null || key == null || key.length() != 1) return Config.ACTION_NONE;
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
        config.disabledKeys = removeKey(config.disabledKeys, key);
        if (action == Config.ACTION_DISABLE) {
            config.disabledKeys = normalizeKeys((config.disabledKeys == null ? "" : config.disabledKeys) + key);
        } else if (action != Config.ACTION_NONE) {
            setKeyForAction(config, action, key);
        }
        config.rebuildActionMap();
    }

    static void restoreDefaults(Config config) {
        if (config == null) return;
        for (int action : QWERTY_ACTIONS) setKeyForAction(config, action, "");
        config.selectAll = "z";
        config.cut = "x";
        config.copy = "c";
        config.paste = "v";
        config.disabledKeys = "";
        config.rebuildActionMap();
    }

    static void clearQwerty(Config config) {
        if (config == null) return;
        for (int action : QWERTY_ACTIONS) setKeyForAction(config, action, "");
        config.disabledKeys = "";
        config.rebuildActionMap();
    }

    static String keyForAction(Config config, int action) {
        switch (action) {
            case Config.ACTION_SELECT_ALL: return config.selectAll;
            case Config.ACTION_CUT: return config.cut;
            case Config.ACTION_COPY: return config.copy;
            case Config.ACTION_PASTE: return config.paste;
            case Config.ACTION_COPY_ALL: return config.copyAll;
            case Config.ACTION_CUT_ALL: return config.cutAll;
            case Config.ACTION_PARAGRAPH_START: return config.paragraphStart;
            case Config.ACTION_PARAGRAPH_END: return config.paragraphEnd;
            case Config.ACTION_SELECT_TO_PARAGRAPH_START: return config.selectToParagraphStart;
            case Config.ACTION_SELECT_TO_PARAGRAPH_END: return config.selectToParagraphEnd;
            case Config.ACTION_OPEN_CLIPBOARD: return config.openClipboard;
            case Config.ACTION_OPEN_QUICK_PHRASE: return config.openQuickPhrase;
            case Config.ACTION_UNDO: return config.undo;
            case Config.ACTION_REDO: return config.redo;
            case Config.ACTION_DOCUMENT_START: return config.documentStart;
            case Config.ACTION_DOCUMENT_END: return config.documentEnd;
            case Config.ACTION_SELECT_TO_DOCUMENT_START: return config.selectToDocumentStart;
            case Config.ACTION_SELECT_TO_DOCUMENT_END: return config.selectToDocumentEnd;
            default: return "";
        }
    }

    static void setKeyForAction(Config config, int action, String key) {
        String value = key == null ? "" : key;
        switch (action) {
            case Config.ACTION_SELECT_ALL: config.selectAll = value; break;
            case Config.ACTION_CUT: config.cut = value; break;
            case Config.ACTION_COPY: config.copy = value; break;
            case Config.ACTION_PASTE: config.paste = value; break;
            case Config.ACTION_COPY_ALL: config.copyAll = value; break;
            case Config.ACTION_CUT_ALL: config.cutAll = value; break;
            case Config.ACTION_PARAGRAPH_START: config.paragraphStart = value; break;
            case Config.ACTION_PARAGRAPH_END: config.paragraphEnd = value; break;
            case Config.ACTION_SELECT_TO_PARAGRAPH_START: config.selectToParagraphStart = value; break;
            case Config.ACTION_SELECT_TO_PARAGRAPH_END: config.selectToParagraphEnd = value; break;
            case Config.ACTION_OPEN_CLIPBOARD: config.openClipboard = value; break;
            case Config.ACTION_OPEN_QUICK_PHRASE: config.openQuickPhrase = value; break;
            case Config.ACTION_UNDO: config.undo = value; break;
            case Config.ACTION_REDO: config.redo = value; break;
            case Config.ACTION_DOCUMENT_START: config.documentStart = value; break;
            case Config.ACTION_DOCUMENT_END: config.documentEnd = value; break;
            case Config.ACTION_SELECT_TO_DOCUMENT_START: config.selectToDocumentStart = value; break;
            case Config.ACTION_SELECT_TO_DOCUMENT_END: config.selectToDocumentEnd = value; break;
            default: break;
        }
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
