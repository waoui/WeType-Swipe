package com.rww.wetypeswipe;

import java.util.Arrays;
import java.util.Locale;

final class Config {
    static final String ACTION_DIAGNOSTIC = "com.rww.wetypeswipe.DIAGNOSTIC";
    static final String ACTION_CONFIG_CHANGED = "com.rww.wetypeswipe.CONFIG_CHANGED";
    static final String PREFS = "gesture_config";

    static final String KEY_SELECT_ALL = "select_all";
    static final String KEY_CUT = "cut";
    static final String KEY_COPY = "copy";
    static final String KEY_PASTE = "paste";
    static final String KEY_DISABLED_KEYS = "disabled_keys";
    static final String KEY_THRESHOLD = "threshold";
    static final String KEY_VIBRATION = "vibration";
    static final String KEY_DIAGNOSTIC = "diagnostic";
    static final String KEY_HIDE_ICON = "hide_icon";

    static final String DIAG_STATUS = "diag_status";
    static final String DIAG_LAST_KEY = "diag_last_key";
    static final String DIAG_LAST_ACTION = "diag_last_action";
    static final String DIAG_LAST_ERROR = "diag_last_error";
    static final String DIAG_UPDATED_AT = "diag_updated_at";

    static final int ACTION_NONE = 0;
    static final int ACTION_SELECT_ALL = 1;
    static final int ACTION_CUT = 2;
    static final int ACTION_COPY = 3;
    static final int ACTION_PASTE = 4;
    static final int ACTION_DISABLE = 5;

    String selectAll = "z";
    String cut = "x";
    String copy = "c";
    String paste = "v";
    String disabledKeys = "";
    int thresholdDp = 12;
    boolean vibration = true;
    boolean diagnostic = false;

    private final int[] actionMap = new int[26];
    private boolean hasAnyBinding;

    void rebuildActionMap() {
        Arrays.fill(actionMap, ACTION_NONE);
        bind(selectAll, ACTION_SELECT_ALL);
        bind(cut, ACTION_CUT);
        bind(copy, ACTION_COPY);
        bind(paste, ACTION_PASTE);
        bindDisabled(disabledKeys);

        hasAnyBinding = false;
        for (int action : actionMap) {
            if (action != ACTION_NONE) {
                hasAnyBinding = true;
                break;
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

    int actionFor(String key) {
        int index = indexOfKey(key);
        return index >= 0 ? actionMap[index] : ACTION_NONE;
    }

    boolean hasAnyBinding() {
        return hasAnyBinding;
    }

    static int menuIdFor(int action) {
        if (action == ACTION_SELECT_ALL) return android.R.id.selectAll;
        if (action == ACTION_CUT) return android.R.id.cut;
        if (action == ACTION_COPY) return android.R.id.copy;
        if (action == ACTION_PASTE) return android.R.id.paste;
        return 0;
    }

    static String actionName(int action) {
        switch (action) {
            case ACTION_SELECT_ALL: return "全选";
            case ACTION_CUT: return "剪切";
            case ACTION_COPY: return "复制";
            case ACTION_PASTE: return "粘贴";
            case ACTION_DISABLE: return "禁用下滑";
            default: return "未绑定";
        }
    }
}
