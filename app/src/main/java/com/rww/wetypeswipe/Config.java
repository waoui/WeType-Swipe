package com.rww.wetypeswipe;

import java.util.Arrays;
import java.util.Locale;

final class Config {
    static final String ACTION_CONFIG_CHANGED = "com.rww.wetypeswipe.CONFIG_CHANGED";
    static final String PREFS = "gesture_config";
    static final String TARGET_CACHE_PREFS = "wetype_swipe_module_cache_v1";
    static final String EXTRA_SNAPSHOT = "config_snapshot";

    static final String KEY_SELECT_ALL = "select_all";
    static final String KEY_CUT = "cut";
    static final String KEY_COPY = "copy";
    static final String KEY_PASTE = "paste";
    static final String KEY_PARAGRAPH_START = "paragraph_start";
    static final String KEY_PARAGRAPH_END = "paragraph_end";
    static final String KEY_SELECT_TO_PARAGRAPH_START = "select_to_paragraph_start";
    static final String KEY_SELECT_TO_PARAGRAPH_END = "select_to_paragraph_end";
    static final String KEY_OPEN_CLIPBOARD = "open_clipboard";
    static final String KEY_OPEN_QUICK_PHRASE = "open_quick_phrase";
    static final String KEY_DISABLED_KEYS = "disabled_keys";
    static final String KEY_THRESHOLD = "threshold";
    static final String KEY_T9_THRESHOLD = "t9_threshold";
    static final String KEY_VIBRATION = "vibration";
    static final String KEY_SHOW_KEY_LABELS = "show_key_labels";
    static final String KEY_SHOW_TRIGGER_HINT = "show_trigger_hint";
    static final String KEY_HIDE_ICON = "hide_icon";
    static final String KEY_REVISION = "revision";

    static final String KEY_T9_2 = "t9_key_2";
    static final String KEY_T9_3 = "t9_key_3";
    static final String KEY_T9_4 = "t9_key_4";
    static final String KEY_T9_5 = "t9_key_5";
    static final String KEY_T9_6 = "t9_key_6";
    static final String KEY_T9_7 = "t9_key_7";
    static final String KEY_T9_8 = "t9_key_8";
    static final String KEY_T9_9 = "t9_key_9";

    static final int ACTION_NONE = 0;
    static final int ACTION_SELECT_ALL = 1;
    static final int ACTION_CUT = 2;
    static final int ACTION_COPY = 3;
    static final int ACTION_PASTE = 4;
    // Keep 5 stable for backward compatibility with existing saved T9 mappings.
    static final int ACTION_DISABLE = 5;
    static final int ACTION_PARAGRAPH_START = 6;
    static final int ACTION_PARAGRAPH_END = 7;
    static final int ACTION_SELECT_TO_PARAGRAPH_START = 8;
    static final int ACTION_SELECT_TO_PARAGRAPH_END = 9;
    static final int ACTION_OPEN_CLIPBOARD = 10;
    static final int ACTION_OPEN_QUICK_PHRASE = 11;

    static final String[] ACTION_MENU_LABELS = {
            "未绑定", "全选", "剪切", "复制", "粘贴",
            "段首", "段尾", "选至段首", "选至段尾",
            "剪贴板", "快捷发送", "禁用下滑"
    };

    private static final int[] ACTION_MENU_VALUES = {
            ACTION_NONE,
            ACTION_SELECT_ALL,
            ACTION_CUT,
            ACTION_COPY,
            ACTION_PASTE,
            ACTION_PARAGRAPH_START,
            ACTION_PARAGRAPH_END,
            ACTION_SELECT_TO_PARAGRAPH_START,
            ACTION_SELECT_TO_PARAGRAPH_END,
            ACTION_OPEN_CLIPBOARD,
            ACTION_OPEN_QUICK_PHRASE,
            ACTION_DISABLE
    };

    String selectAll = "z";
    String cut = "x";
    String copy = "c";
    String paste = "v";
    String paragraphStart = "";
    String paragraphEnd = "";
    String selectToParagraphStart = "";
    String selectToParagraphEnd = "";
    String openClipboard = "";
    String openQuickPhrase = "";
    String disabledKeys = "";
    int thresholdDp = 12;
    int t9ThresholdDp = 20;
    boolean vibration = true;
    boolean showKeyLabels = true;
    boolean showTriggerHint = true;
    int revision = 0;

    final int[] t9Actions = new int[10];
    private final int[] actionMap = new int[26];
    private boolean hasAnyBinding;

    void rebuildActionMap() {
        Arrays.fill(actionMap, ACTION_NONE);
        bind(selectAll, ACTION_SELECT_ALL);
        bind(cut, ACTION_CUT);
        bind(copy, ACTION_COPY);
        bind(paste, ACTION_PASTE);
        bind(paragraphStart, ACTION_PARAGRAPH_START);
        bind(paragraphEnd, ACTION_PARAGRAPH_END);
        bind(selectToParagraphStart, ACTION_SELECT_TO_PARAGRAPH_START);
        bind(selectToParagraphEnd, ACTION_SELECT_TO_PARAGRAPH_END);
        bind(openClipboard, ACTION_OPEN_CLIPBOARD);
        bind(openQuickPhrase, ACTION_OPEN_QUICK_PHRASE);
        bindDisabled(disabledKeys);

        hasAnyBinding = false;
        for (int action : actionMap) {
            if (action != ACTION_NONE) {
                hasAnyBinding = true;
                break;
            }
        }
        if (!hasAnyBinding) {
            for (int digit = 2; digit <= 9; digit++) {
                if (validAction(t9Actions[digit]) != ACTION_NONE) {
                    hasAnyBinding = true;
                    break;
                }
            }
        }
    }

    private void bind(String key, int action) {
        int index = indexOfKey(key);
        if (index >= 0) actionMap[index] = action;
    }

    private void bindDisabled(String keys) {
        if (keys == null) return;
        String normalized = keys.toLowerCase(Locale.ROOT);
        for (int i = 0; i < normalized.length(); i++) {
            char c = normalized.charAt(i);
            if (c < 'a' || c > 'z') continue;
            int index = c - 'a';
            if (actionMap[index] == ACTION_NONE) actionMap[index] = ACTION_DISABLE;
        }
    }

    private static int indexOfKey(String key) {
        if (key == null) return -1;
        String normalized = key.trim().toLowerCase(Locale.ROOT);
        if (normalized.length() != 1) return -1;
        char c = normalized.charAt(0);
        return c >= 'a' && c <= 'z' ? c - 'a' : -1;
    }

    int actionFor(String key, boolean t9) {
        if (t9) {
            if (key == null || key.length() != 1) return ACTION_NONE;
            char c = key.charAt(0);
            if (c < '2' || c > '9') return ACTION_NONE;
            return validAction(t9Actions[c - '0']);
        }
        int index = indexOfKey(key);
        return index >= 0 ? actionMap[index] : ACTION_NONE;
    }

    boolean hasAnyBinding() {
        return hasAnyBinding;
    }

    static int validAction(int action) {
        return action >= ACTION_NONE && action <= ACTION_OPEN_QUICK_PHRASE
                ? action : ACTION_NONE;
    }

    static int menuPositionForAction(int action) {
        int checked = validAction(action);
        for (int i = 0; i < ACTION_MENU_VALUES.length; i++) {
            if (ACTION_MENU_VALUES[i] == checked) return i;
        }
        return 0;
    }

    static int actionForMenuPosition(int position) {
        return position >= 0 && position < ACTION_MENU_VALUES.length
                ? ACTION_MENU_VALUES[position] : ACTION_NONE;
    }

    static String t9PrefKey(int digit) {
        switch (digit) {
            case 2: return KEY_T9_2;
            case 3: return KEY_T9_3;
            case 4: return KEY_T9_4;
            case 5: return KEY_T9_5;
            case 6: return KEY_T9_6;
            case 7: return KEY_T9_7;
            case 8: return KEY_T9_8;
            case 9: return KEY_T9_9;
            default: throw new IllegalArgumentException("digit must be 2..9");
        }
    }

    static String t9Label(int digit) {
        switch (digit) {
            case 2: return "2 / ABC";
            case 3: return "3 / DEF";
            case 4: return "4 / GHI";
            case 5: return "5 / JKL";
            case 6: return "6 / MNO";
            case 7: return "7 / PQRS";
            case 8: return "8 / TUV";
            case 9: return "9 / WXYZ";
            default: return String.valueOf(digit);
        }
    }

    static int menuIdFor(int action) {
        if (action == ACTION_SELECT_ALL) return android.R.id.selectAll;
        if (action == ACTION_CUT) return android.R.id.cut;
        if (action == ACTION_COPY) return android.R.id.copy;
        if (action == ACTION_PASTE) return android.R.id.paste;
        return 0;
    }

    static String actionName(int action) {
        switch (validAction(action)) {
            case ACTION_SELECT_ALL: return "全选";
            case ACTION_CUT: return "剪切";
            case ACTION_COPY: return "复制";
            case ACTION_PASTE: return "粘贴";
            case ACTION_DISABLE: return "禁用下滑";
            case ACTION_PARAGRAPH_START: return "段首";
            case ACTION_PARAGRAPH_END: return "段尾";
            case ACTION_SELECT_TO_PARAGRAPH_START: return "选至段首";
            case ACTION_SELECT_TO_PARAGRAPH_END: return "选至段尾";
            case ACTION_OPEN_CLIPBOARD: return "剪贴板";
            case ACTION_OPEN_QUICK_PHRASE: return "快捷发送";
            default: return "未绑定";
        }
    }
}
