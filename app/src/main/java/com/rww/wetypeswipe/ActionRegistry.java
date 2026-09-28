package com.rww.wetypeswipe;

/** Single source of truth for action metadata and QWERTY-backed config fields. */
final class ActionRegistry {
    static final int FLAG_QWERTY = 1;
    static final int FLAG_INPUT_METHOD = 1 << 1;
    static final int FLAG_NATIVE_PANEL = 1 << 2;
    static final int FLAG_DOCUMENT = 1 << 3;
    static final int FLAG_PARAGRAPH = 1 << 4;
    static final int FLAG_COMPOUND = 1 << 5;
    static final int FLAG_HISTORY = 1 << 6;
    static final int FLAG_PASSWORD_ALLOWED = 1 << 7;

    interface KeyGetter { String get(Config config); }
    interface KeySetter { void set(Config config, String value); }

    static final class Spec {
        final int id;
        final String name;
        final String shortLabel;
        final String storageKey;
        final int flags;
        final KeyGetter getter;
        final KeySetter setter;

        Spec(int id, String name, String shortLabel, String storageKey, int flags,
             KeyGetter getter, KeySetter setter) {
            this.id = id;
            this.name = name;
            this.shortLabel = shortLabel;
            this.storageKey = storageKey;
            this.flags = flags;
            this.getter = getter;
            this.setter = setter;
        }

        boolean has(int flag) { return (flags & flag) != 0; }
    }

    private static final Spec[] BY_ID = new Spec[24];

    private static final int[] MENU_ORDER = {
            Config.ACTION_NONE,
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
            Config.ACTION_DOCUMENT_START,
            Config.ACTION_DOCUMENT_END,
            Config.ACTION_SELECT_TO_DOCUMENT_START,
            Config.ACTION_SELECT_TO_DOCUMENT_END,
            Config.ACTION_OPEN_CLIPBOARD,
            Config.ACTION_OPEN_QUICK_PHRASE,
            Config.ACTION_UNDO,
            Config.ACTION_REDO,
            Config.ACTION_INSERT_TEXT,
            Config.ACTION_NEXT_INPUT_METHOD,
            Config.ACTION_PREVIOUS_INPUT_METHOD,
            Config.ACTION_SHOW_INPUT_METHOD_PICKER,
            Config.ACTION_DISABLE
    };

    private static final int[] QWERTY_ORDER = {
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
            Config.ACTION_SELECT_TO_DOCUMENT_END,
            Config.ACTION_NEXT_INPUT_METHOD,
            Config.ACTION_PREVIOUS_INPUT_METHOD,
            Config.ACTION_SHOW_INPUT_METHOD_PICKER
    };

    static {
        put(simple(Config.ACTION_NONE, "未绑定", ""));
        put(qwerty(Config.ACTION_SELECT_ALL, "全选", "全选", Config.KEY_SELECT_ALL,
                c -> c.selectAll, (c, v) -> c.selectAll = v, 0));
        put(qwerty(Config.ACTION_CUT, "剪切", "剪切", Config.KEY_CUT,
                c -> c.cut, (c, v) -> c.cut = v, 0));
        put(qwerty(Config.ACTION_COPY, "复制", "复制", Config.KEY_COPY,
                c -> c.copy, (c, v) -> c.copy = v, 0));
        put(qwerty(Config.ACTION_PASTE, "粘贴", "粘贴", Config.KEY_PASTE,
                c -> c.paste, (c, v) -> c.paste = v, 0));
        put(simple(Config.ACTION_DISABLE, "禁用下滑", ""));
        put(qwerty(Config.ACTION_PARAGRAPH_START, "段首", "段首", Config.KEY_PARAGRAPH_START,
                c -> c.paragraphStart, (c, v) -> c.paragraphStart = v, FLAG_PARAGRAPH));
        put(qwerty(Config.ACTION_PARAGRAPH_END, "段尾", "段尾", Config.KEY_PARAGRAPH_END,
                c -> c.paragraphEnd, (c, v) -> c.paragraphEnd = v, FLAG_PARAGRAPH));
        put(qwerty(Config.ACTION_SELECT_TO_PARAGRAPH_START, "选至段首", "选前",
                Config.KEY_SELECT_TO_PARAGRAPH_START,
                c -> c.selectToParagraphStart, (c, v) -> c.selectToParagraphStart = v,
                FLAG_PARAGRAPH));
        put(qwerty(Config.ACTION_SELECT_TO_PARAGRAPH_END, "选至段尾", "选后",
                Config.KEY_SELECT_TO_PARAGRAPH_END,
                c -> c.selectToParagraphEnd, (c, v) -> c.selectToParagraphEnd = v,
                FLAG_PARAGRAPH));
        put(qwerty(Config.ACTION_OPEN_CLIPBOARD, "剪贴板", "剪贴", Config.KEY_OPEN_CLIPBOARD,
                c -> c.openClipboard, (c, v) -> c.openClipboard = v, FLAG_NATIVE_PANEL));
        put(qwerty(Config.ACTION_OPEN_QUICK_PHRASE, "快捷发送", "快捷", Config.KEY_OPEN_QUICK_PHRASE,
                c -> c.openQuickPhrase, (c, v) -> c.openQuickPhrase = v, FLAG_NATIVE_PANEL));
        put(qwerty(Config.ACTION_COPY_ALL, "复制全部", "全复制", Config.KEY_COPY_ALL,
                c -> c.copyAll, (c, v) -> c.copyAll = v, FLAG_COMPOUND));
        put(qwerty(Config.ACTION_CUT_ALL, "剪切全部", "全剪切", Config.KEY_CUT_ALL,
                c -> c.cutAll, (c, v) -> c.cutAll = v, FLAG_COMPOUND));
        put(qwerty(Config.ACTION_UNDO, "撤销", "撤销", Config.KEY_UNDO,
                c -> c.undo, (c, v) -> c.undo = v, FLAG_HISTORY));
        put(qwerty(Config.ACTION_REDO, "重做", "重做", Config.KEY_REDO,
                c -> c.redo, (c, v) -> c.redo = v, FLAG_HISTORY));
        put(qwerty(Config.ACTION_DOCUMENT_START, "文首", "文首", Config.KEY_DOCUMENT_START,
                c -> c.documentStart, (c, v) -> c.documentStart = v, FLAG_DOCUMENT));
        put(qwerty(Config.ACTION_DOCUMENT_END, "文尾", "文尾", Config.KEY_DOCUMENT_END,
                c -> c.documentEnd, (c, v) -> c.documentEnd = v, FLAG_DOCUMENT));
        put(qwerty(Config.ACTION_SELECT_TO_DOCUMENT_START, "选至文首", "选文首",
                Config.KEY_SELECT_TO_DOCUMENT_START,
                c -> c.selectToDocumentStart, (c, v) -> c.selectToDocumentStart = v,
                FLAG_DOCUMENT));
        put(qwerty(Config.ACTION_SELECT_TO_DOCUMENT_END, "选至文尾", "选文尾",
                Config.KEY_SELECT_TO_DOCUMENT_END,
                c -> c.selectToDocumentEnd, (c, v) -> c.selectToDocumentEnd = v,
                FLAG_DOCUMENT));
        put(simple(Config.ACTION_INSERT_TEXT, "输入指定内容", "文本"));
        put(qwerty(Config.ACTION_NEXT_INPUT_METHOD, "下一个输入法", "下个输入",
                Config.KEY_NEXT_INPUT_METHOD,
                c -> c.nextInputMethod, (c, v) -> c.nextInputMethod = v,
                FLAG_INPUT_METHOD | FLAG_PASSWORD_ALLOWED));
        put(qwerty(Config.ACTION_PREVIOUS_INPUT_METHOD, "上一个输入法", "上个输入",
                Config.KEY_PREVIOUS_INPUT_METHOD,
                c -> c.previousInputMethod, (c, v) -> c.previousInputMethod = v,
                FLAG_INPUT_METHOD | FLAG_PASSWORD_ALLOWED));
        put(qwerty(Config.ACTION_SHOW_INPUT_METHOD_PICKER, "选择输入法", "选输入法",
                Config.KEY_SHOW_INPUT_METHOD_PICKER,
                c -> c.showInputMethodPicker, (c, v) -> c.showInputMethodPicker = v,
                FLAG_INPUT_METHOD | FLAG_PASSWORD_ALLOWED));
    }

    private ActionRegistry() {}

    private static Spec simple(int id, String name, String shortLabel) {
        return new Spec(id, name, shortLabel, null, 0, null, null);
    }

    private static Spec qwerty(int id, String name, String shortLabel, String storageKey,
                               KeyGetter getter, KeySetter setter, int extraFlags) {
        return new Spec(id, name, shortLabel, storageKey, FLAG_QWERTY | extraFlags, getter, setter);
    }

    private static void put(Spec spec) {
        if (spec.id < 0 || spec.id >= BY_ID.length || BY_ID[spec.id] != null) {
            throw new IllegalStateException("invalid or duplicate action id " + spec.id);
        }
        BY_ID[spec.id] = spec;
    }

    static Spec spec(int action) {
        return action >= 0 && action < BY_ID.length ? BY_ID[action] : null;
    }

    static int validAction(int action) {
        return spec(action) == null ? Config.ACTION_NONE : action;
    }

    static String name(int action) {
        Spec spec = spec(validAction(action));
        return spec == null ? "未绑定" : spec.name;
    }

    static String shortLabel(int action) {
        Spec spec = spec(validAction(action));
        return spec == null ? "" : spec.shortLabel;
    }

    static boolean hasFlag(int action, int flag) {
        Spec spec = spec(validAction(action));
        return spec != null && spec.has(flag);
    }

    static boolean isInputMethodAction(int action) { return hasFlag(action, FLAG_INPUT_METHOD); }
    static boolean isNativePanelAction(int action) { return hasFlag(action, FLAG_NATIVE_PANEL); }
    static boolean isDocumentAction(int action) { return hasFlag(action, FLAG_DOCUMENT); }
    static boolean isParagraphAction(int action) { return hasFlag(action, FLAG_PARAGRAPH); }
    static boolean isCompoundAction(int action) { return hasFlag(action, FLAG_COMPOUND); }
    static boolean isEditorHistoryAction(int action) { return hasFlag(action, FLAG_HISTORY); }
    static boolean allowsInPassword(int action) { return hasFlag(action, FLAG_PASSWORD_ALLOWED); }

    static int[] qwertyActions() { return QWERTY_ORDER.clone(); }

    static String[] qwertyLabels() {
        String[] result = new String[QWERTY_ORDER.length];
        for (int i = 0; i < result.length; i++) result[i] = name(QWERTY_ORDER[i]);
        return result;
    }

    static String[] menuLabels() {
        String[] result = new String[MENU_ORDER.length];
        for (int i = 0; i < result.length; i++) result[i] = name(MENU_ORDER[i]);
        return result;
    }

    static int menuPositionForAction(int action) {
        int checked = validAction(action);
        for (int i = 0; i < MENU_ORDER.length; i++) if (MENU_ORDER[i] == checked) return i;
        return 0;
    }

    static int actionForMenuPosition(int position) {
        return position >= 0 && position < MENU_ORDER.length
                ? MENU_ORDER[position] : Config.ACTION_NONE;
    }

    static String storageKey(int action) {
        Spec spec = spec(action);
        return spec == null ? null : spec.storageKey;
    }

    static String keyFor(Config config, int action) {
        Spec spec = spec(action);
        return config == null || spec == null || spec.getter == null ? "" : spec.getter.get(config);
    }

    static void setKey(Config config, int action, String value) {
        Spec spec = spec(action);
        if (config != null && spec != null && spec.setter != null) {
            spec.setter.set(config, value == null ? "" : value);
        }
    }

    static int registeredCount() {
        int count = 0;
        for (Spec spec : BY_ID) if (spec != null) count++;
        return count;
    }

    static int[] registeredIds() {
        int[] ids = new int[registeredCount()];
        int at = 0;
        for (Spec spec : BY_ID) if (spec != null) ids[at++] = spec.id;
        return ids;
    }

    static int menuCount() { return MENU_ORDER.length; }

    static boolean qwertyContains(int action) {
        for (int value : QWERTY_ORDER) if (value == action) return true;
        return false;
    }
}
