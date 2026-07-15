from pathlib import Path
import re


def replace_once(text: str, old: str, new: str, name: str) -> str:
    if old not in text:
        raise RuntimeError(f"missing patch anchor: {name}")
    return text.replace(old, new, 1)


# Config.java
path = Path("app/src/main/java/com/rww/wetypeswipe/Config.java")
text = path.read_text(encoding="utf-8")
text = replace_once(text,
'''    static final String KEY_COPY = "copy";
    static final String KEY_PASTE = "paste";''',
'''    static final String KEY_COPY = "copy";
    static final String KEY_PASTE = "paste";
    static final String KEY_COPY_ALL = "copy_all";
    static final String KEY_CUT_ALL = "cut_all";''', "config action keys")
text = replace_once(text,
'''    static final String KEY_REVISION = "revision";
''',
'''    static final String KEY_REVISION = "revision";
    static final String KEY_QWERTY_LABEL_PREFIX = "qwerty_label_";
    static final String KEY_T9_LABEL_PREFIX = "t9_label_";
    static final String LABEL_HIDDEN = "__HIDDEN__";
''', "config label keys")
text = replace_once(text,
'''    static final int ACTION_OPEN_CLIPBOARD = 10;
    static final int ACTION_OPEN_QUICK_PHRASE = 11;
''',
'''    static final int ACTION_OPEN_CLIPBOARD = 10;
    static final int ACTION_OPEN_QUICK_PHRASE = 11;
    static final int ACTION_COPY_ALL = 12;
    static final int ACTION_CUT_ALL = 13;
''', "config action ids")
text = replace_once(text,
'''            "未绑定", "全选", "剪切", "复制", "粘贴",
            "段首", "段尾", "选至段首", "选至段尾",
            "剪贴板", "快捷发送", "禁用下滑"''',
'''            "未绑定", "全选", "剪切", "复制", "粘贴",
            "复制全部", "剪切全部",
            "段首", "段尾", "选至段首", "选至段尾",
            "剪贴板", "快捷发送", "禁用下滑"''', "config menu labels")
text = replace_once(text,
'''            ACTION_PASTE,
            ACTION_PARAGRAPH_START,''',
'''            ACTION_PASTE,
            ACTION_COPY_ALL,
            ACTION_CUT_ALL,
            ACTION_PARAGRAPH_START,''', "config menu values")
text = replace_once(text,
'''    String paste = "v";
    String paragraphStart = "";''',
'''    String paste = "v";
    String copyAll = "";
    String cutAll = "";
    String paragraphStart = "";''', "config fields")
text = replace_once(text,
'''    final int[] t9Actions = new int[10];
    private final int[] actionMap = new int[26];''',
'''    final int[] t9Actions = new int[10];
    final String[] qwertyLabels = new String[26];
    final String[] t9Labels = new String[10];
    private final int[] actionMap = new int[26];''', "config label arrays")
text = replace_once(text,
'''        bind(paste, ACTION_PASTE);
        bind(paragraphStart, ACTION_PARAGRAPH_START);''',
'''        bind(paste, ACTION_PASTE);
        bind(copyAll, ACTION_COPY_ALL);
        bind(cutAll, ACTION_CUT_ALL);
        bind(paragraphStart, ACTION_PARAGRAPH_START);''', "config action map")
text = replace_once(text,
'''        return action >= ACTION_NONE && action <= ACTION_OPEN_QUICK_PHRASE
                ? action : ACTION_NONE;''',
'''        return action >= ACTION_NONE && action <= ACTION_CUT_ALL
                ? action : ACTION_NONE;''', "config valid action")
text = replace_once(text,
'''    static String t9PrefKey(int digit) {''',
'''    static String qwertyLabelPrefKey(char key) {
        if (key < 'a' || key > 'z') throw new IllegalArgumentException("key must be a..z");
        return KEY_QWERTY_LABEL_PREFIX + key;
    }

    static String t9LabelPrefKey(int digit) {
        if (digit < 2 || digit > 9) throw new IllegalArgumentException("digit must be 2..9");
        return KEY_T9_LABEL_PREFIX + digit;
    }

    static String normalizeLabelValue(String value) {
        if (value == null) return "";
        if (LABEL_HIDDEN.equals(value)) return LABEL_HIDDEN;
        String clean = value.replace('\n', ' ').replace('\r', ' ').trim();
        int count = clean.codePointCount(0, clean.length());
        if (count > 4) clean = clean.substring(0, clean.offsetByCodePoints(0, 4));
        return clean;
    }

    String labelFor(String key, boolean t9, int action) {
        String configured = "";
        if (key != null && key.length() == 1) {
            char value = Character.toLowerCase(key.charAt(0));
            if (t9 && value >= '2' && value <= '9') configured = t9Labels[value - '0'];
            else if (!t9 && value >= 'a' && value <= 'z') configured = qwertyLabels[value - 'a'];
        }
        configured = normalizeLabelValue(configured);
        if (LABEL_HIDDEN.equals(configured)) return "";
        if (!configured.isEmpty()) return configured;
        return shortActionLabel(action);
    }

    static String shortActionLabel(int action) {
        switch (validAction(action)) {
            case ACTION_SELECT_ALL: return "全选";
            case ACTION_CUT: return "剪切";
            case ACTION_COPY: return "复制";
            case ACTION_PASTE: return "粘贴";
            case ACTION_COPY_ALL: return "全复制";
            case ACTION_CUT_ALL: return "全剪切";
            case ACTION_PARAGRAPH_START: return "段首";
            case ACTION_PARAGRAPH_END: return "段尾";
            case ACTION_SELECT_TO_PARAGRAPH_START: return "选前";
            case ACTION_SELECT_TO_PARAGRAPH_END: return "选后";
            case ACTION_OPEN_CLIPBOARD: return "剪贴";
            case ACTION_OPEN_QUICK_PHRASE: return "快捷";
            default: return "";
        }
    }

    static String t9PrefKey(int digit) {''', "config label helpers")
text = replace_once(text,
'''            case ACTION_PASTE: return "粘贴";
            case ACTION_DISABLE: return "禁用下滑";''',
'''            case ACTION_PASTE: return "粘贴";
            case ACTION_COPY_ALL: return "复制全部";
            case ACTION_CUT_ALL: return "剪切全部";
            case ACTION_DISABLE: return "禁用下滑";''', "config action names")
path.write_text(text, encoding="utf-8")


# MainActivity.java
path = Path("app/src/main/java/com/rww/wetypeswipe/MainActivity.java")
text = path.read_text(encoding="utf-8")
text = replace_once(text,
'''import android.widget.CheckBox;
import android.widget.LinearLayout;''',
'''import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.LinearLayout;''', "activity EditText import")
text = replace_once(text,
'''import android.os.Bundle;
import android.view.Gravity;''',
'''import android.os.Bundle;
import android.text.InputFilter;
import android.view.Gravity;''', "activity InputFilter import")
text = replace_once(text,
'''            Config.ACTION_COPY,
            Config.ACTION_PASTE,
            Config.ACTION_PARAGRAPH_START,''',
'''            Config.ACTION_COPY,
            Config.ACTION_PASTE,
            Config.ACTION_COPY_ALL,
            Config.ACTION_CUT_ALL,
            Config.ACTION_PARAGRAPH_START,''', "activity action list")
text = replace_once(text,
'''            "全选", "剪切", "复制", "粘贴",
            "段首", "段尾", "选至段首", "选至段尾",''',
'''            "全选", "剪切", "复制", "粘贴", "复制全部", "剪切全部",
            "段首", "段尾", "选至段首", "选至段尾",''', "activity action labels")
text = replace_once(text,
'''    private final LinearLayout[] qwertyKeyViews = new LinearLayout[26];
    private String disabledKeys = "";''',
'''    private final LinearLayout[] qwertyKeyViews = new LinearLayout[26];
    private final String[] qwertyCustomLabels = new String[26];
    private String disabledKeys = "";''', "activity qwerty labels")
text = replace_once(text,
'''    private final LinearLayout[] t9KeyViews = new LinearLayout[10];
''',
'''    private final LinearLayout[] t9KeyViews = new LinearLayout[10];
    private final String[] t9CustomLabels = new String[10];
''', "activity t9 labels")
text = replace_once(text,
'''        TextView version = text("v1.11.0 · 按键功能文字与显示选项", 13, COLOR_SECONDARY);''',
'''        TextView version = text("v1.11.1-test1 · 全复制、全剪切与自定义标签", 13, COLOR_SECONDARY);''', "activity version")
text = replace_once(text,
'''                "按照真实键盘排列展示。点击字母键，直接选择该键下滑时执行的动作。",''',
'''                "点击设置动作，长按设置该按键显示的自定义标签。",''', "activity qwerty subtitle")
text = replace_once(text,
'''        key.setOnClickListener(v -> showQwertyActionDialog(letter));
        return key;''',
'''        key.setOnClickListener(v -> showQwertyActionDialog(letter));
        key.setOnLongClickListener(v -> {
            showQwertyLabelDialog(letter);
            return true;
        });
        return key;''', "activity qwerty long press")
text = replace_once(text,
'''                "按照九宫格键盘排列展示。2–9 可设置，1 保持普通输入。",''',
'''                "2–9 可设置。点击设置动作，长按设置该按键显示标签。",''', "activity t9 subtitle")
text = replace_once(text,
'''            key.setOnClickListener(v -> showT9ActionDialog(digit));
        } else {''',
'''            key.setOnClickListener(v -> showT9ActionDialog(digit));
            key.setOnLongClickListener(v -> {
                showT9LabelDialog(digit);
                return true;
            });
        } else {''', "activity t9 long press")

label_dialog_methods = r'''
    private interface LabelValueChanged { void apply(String value); }

    private void showQwertyLabelDialog(char letter) {
        int action = actionForQwertyKey(String.valueOf(letter));
        showLabelDialog(Character.toUpperCase(letter) + " 键显示标签",
                qwertyCustomLabels[letter - 'a'], Config.shortActionLabel(action), value -> {
                    qwertyCustomLabels[letter - 'a'] = value;
                    updateQwertyKeyView(letter);
                });
    }

    private void showT9LabelDialog(int digit) {
        int action = t9Actions[digit];
        showLabelDialog(Config.t9Label(digit) + " 显示标签",
                t9CustomLabels[digit], Config.shortActionLabel(action), value -> {
                    t9CustomLabels[digit] = value;
                    updateT9View(digit);
                });
    }

    private void showLabelDialog(String title, String currentValue,
                                 String automaticValue, LabelValueChanged changed) {
        String current = Config.normalizeLabelValue(currentValue);
        int selected = Config.LABEL_HIDDEN.equals(current) ? 2 : (current.isEmpty() ? 0 : 1);
        String autoText = automaticValue == null || automaticValue.isEmpty()
                ? "自动（当前无动作）" : "自动（" + automaticValue + "）";
        String customText = current.isEmpty() || Config.LABEL_HIDDEN.equals(current)
                ? "自定义文字" : "自定义（" + current + "）";
        String[] options = {autoText, customText, "隐藏此按键标签"};
        AlertDialog dialog = new AlertDialog.Builder(this)
                .setTitle(title)
                .setSingleChoiceItems(options, selected, null)
                .setNegativeButton("取消", null)
                .create();
        dialog.setOnShowListener(ignored -> dialog.getListView().setOnItemClickListener(
                (parent, view, position, id) -> {
                    dialog.dismiss();
                    if (position == 0) changed.apply("");
                    else if (position == 2) changed.apply(Config.LABEL_HIDDEN);
                    else showCustomLabelInput(title, current, changed);
                }));
        dialog.show();
    }

    private void showCustomLabelInput(String title, String currentValue, LabelValueChanged changed) {
        EditText input = new EditText(this);
        String current = Config.normalizeLabelValue(currentValue);
        if (!Config.LABEL_HIDDEN.equals(current)) input.setText(current);
        input.setSingleLine(true);
        input.setHint("最多 4 个字符，留空恢复自动");
        input.setFilters(new InputFilter[]{new InputFilter.LengthFilter(4)});
        input.setSelectAllOnFocus(true);
        int padding = dp(20);
        LinearLayout host = vertical();
        host.setPadding(padding, dp(8), padding, 0);
        host.addView(input, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        AlertDialog dialog = new AlertDialog.Builder(this)
                .setTitle(title + " · 自定义")
                .setView(host)
                .setNegativeButton("取消", null)
                .setPositiveButton("保存", null)
                .create();
        dialog.setOnShowListener(ignored -> dialog.getButton(AlertDialog.BUTTON_POSITIVE)
                .setOnClickListener(v -> {
                    String value = Config.normalizeLabelValue(input.getText().toString());
                    changed.apply(value);
                    dialog.dismiss();
                }));
        dialog.show();
        input.requestFocus();
    }

'''
text = replace_once(text,
'''    private void assignQwertyAction(String key, int action) {''',
label_dialog_methods + '''    private void assignQwertyAction(String key, int action) {''', "activity label dialogs")

text = replace_once(text,
'''        qwertyKeys[4] = normalizedKey(prefs.getString(Config.KEY_PARAGRAPH_START, ""));
        qwertyKeys[5] = normalizedKey(prefs.getString(Config.KEY_PARAGRAPH_END, ""));
        qwertyKeys[6] = normalizedKey(prefs.getString(Config.KEY_SELECT_TO_PARAGRAPH_START, ""));
        qwertyKeys[7] = normalizedKey(prefs.getString(Config.KEY_SELECT_TO_PARAGRAPH_END, ""));
        qwertyKeys[8] = normalizedKey(prefs.getString(Config.KEY_OPEN_CLIPBOARD, ""));
        qwertyKeys[9] = normalizedKey(prefs.getString(Config.KEY_OPEN_QUICK_PHRASE, ""));''',
'''        qwertyKeys[4] = normalizedKey(prefs.getString(Config.KEY_COPY_ALL, ""));
        qwertyKeys[5] = normalizedKey(prefs.getString(Config.KEY_CUT_ALL, ""));
        qwertyKeys[6] = normalizedKey(prefs.getString(Config.KEY_PARAGRAPH_START, ""));
        qwertyKeys[7] = normalizedKey(prefs.getString(Config.KEY_PARAGRAPH_END, ""));
        qwertyKeys[8] = normalizedKey(prefs.getString(Config.KEY_SELECT_TO_PARAGRAPH_START, ""));
        qwertyKeys[9] = normalizedKey(prefs.getString(Config.KEY_SELECT_TO_PARAGRAPH_END, ""));
        qwertyKeys[10] = normalizedKey(prefs.getString(Config.KEY_OPEN_CLIPBOARD, ""));
        qwertyKeys[11] = normalizedKey(prefs.getString(Config.KEY_OPEN_QUICK_PHRASE, ""));''', "activity load actions")
text = replace_once(text,
'''        disabledKeys = normalizedKeys(prefs.getString(Config.KEY_DISABLED_KEYS, ""));
        for (int digit = 2; digit <= 9; digit++) {''',
'''        disabledKeys = normalizedKeys(prefs.getString(Config.KEY_DISABLED_KEYS, ""));
        for (char key = 'a'; key <= 'z'; key++) {
            qwertyCustomLabels[key - 'a'] = Config.normalizeLabelValue(
                    prefs.getString(Config.qwertyLabelPrefKey(key), ""));
        }
        for (int digit = 2; digit <= 9; digit++) {
            t9CustomLabels[digit] = Config.normalizeLabelValue(
                    prefs.getString(Config.t9LabelPrefKey(digit), ""));''', "activity load labels")
text = replace_once(text,
'''                .putString(Config.KEY_PASTE, qwertyKeys[3])
                .putString(Config.KEY_PARAGRAPH_START, qwertyKeys[4])
                .putString(Config.KEY_PARAGRAPH_END, qwertyKeys[5])
                .putString(Config.KEY_SELECT_TO_PARAGRAPH_START, qwertyKeys[6])
                .putString(Config.KEY_SELECT_TO_PARAGRAPH_END, qwertyKeys[7])
                .putString(Config.KEY_OPEN_CLIPBOARD, qwertyKeys[8])
                .putString(Config.KEY_OPEN_QUICK_PHRASE, qwertyKeys[9])''',
'''                .putString(Config.KEY_PASTE, qwertyKeys[3])
                .putString(Config.KEY_COPY_ALL, qwertyKeys[4])
                .putString(Config.KEY_CUT_ALL, qwertyKeys[5])
                .putString(Config.KEY_PARAGRAPH_START, qwertyKeys[6])
                .putString(Config.KEY_PARAGRAPH_END, qwertyKeys[7])
                .putString(Config.KEY_SELECT_TO_PARAGRAPH_START, qwertyKeys[8])
                .putString(Config.KEY_SELECT_TO_PARAGRAPH_END, qwertyKeys[9])
                .putString(Config.KEY_OPEN_CLIPBOARD, qwertyKeys[10])
                .putString(Config.KEY_OPEN_QUICK_PHRASE, qwertyKeys[11])''', "activity save actions")
text = text.replace('''                .remove("copy_all")
                .remove("cut_all")
''', '', 1)
text = replace_once(text,
'''        for (int digit = 2; digit <= 9; digit++) {
            editor.putInt(Config.t9PrefKey(digit), t9Actions[digit]);
        }
''',
'''        for (char key = 'a'; key <= 'z'; key++) {
            editor.putString(Config.qwertyLabelPrefKey(key),
                    Config.normalizeLabelValue(qwertyCustomLabels[key - 'a']));
        }
        for (int digit = 2; digit <= 9; digit++) {
            editor.putInt(Config.t9PrefKey(digit), t9Actions[digit]);
            editor.putString(Config.t9LabelPrefKey(digit),
                    Config.normalizeLabelValue(t9CustomLabels[digit]));
        }
''', "activity save labels")
text = replace_once(text,
'''        changed.putExtra(Config.KEY_PASTE, qwertyKeys[3]);
        changed.putExtra(Config.KEY_PARAGRAPH_START, qwertyKeys[4]);
        changed.putExtra(Config.KEY_PARAGRAPH_END, qwertyKeys[5]);
        changed.putExtra(Config.KEY_SELECT_TO_PARAGRAPH_START, qwertyKeys[6]);
        changed.putExtra(Config.KEY_SELECT_TO_PARAGRAPH_END, qwertyKeys[7]);
        changed.putExtra(Config.KEY_OPEN_CLIPBOARD, qwertyKeys[8]);
        changed.putExtra(Config.KEY_OPEN_QUICK_PHRASE, qwertyKeys[9]);''',
'''        changed.putExtra(Config.KEY_PASTE, qwertyKeys[3]);
        changed.putExtra(Config.KEY_COPY_ALL, qwertyKeys[4]);
        changed.putExtra(Config.KEY_CUT_ALL, qwertyKeys[5]);
        changed.putExtra(Config.KEY_PARAGRAPH_START, qwertyKeys[6]);
        changed.putExtra(Config.KEY_PARAGRAPH_END, qwertyKeys[7]);
        changed.putExtra(Config.KEY_SELECT_TO_PARAGRAPH_START, qwertyKeys[8]);
        changed.putExtra(Config.KEY_SELECT_TO_PARAGRAPH_END, qwertyKeys[9]);
        changed.putExtra(Config.KEY_OPEN_CLIPBOARD, qwertyKeys[10]);
        changed.putExtra(Config.KEY_OPEN_QUICK_PHRASE, qwertyKeys[11]);''', "activity broadcast actions")
text = replace_once(text,
'''        for (int digit = 2; digit <= 9; digit++) {
            changed.putExtra(Config.t9PrefKey(digit), t9Actions[digit]);
        }
''',
'''        for (char key = 'a'; key <= 'z'; key++) {
            changed.putExtra(Config.qwertyLabelPrefKey(key),
                    Config.normalizeLabelValue(qwertyCustomLabels[key - 'a']));
        }
        for (int digit = 2; digit <= 9; digit++) {
            changed.putExtra(Config.t9PrefKey(digit), t9Actions[digit]);
            changed.putExtra(Config.t9LabelPrefKey(digit),
                    Config.normalizeLabelValue(t9CustomLabels[digit]));
        }
''', "activity broadcast labels")
text = replace_once(text,
'''        int action = actionForQwertyKey(String.valueOf(letter));
        actionView.setText(shortActionName(action));''',
'''        int action = actionForQwertyKey(String.valueOf(letter));
        actionView.setText(previewLabel(qwertyCustomLabels[index], action));''', "activity qwerty preview")
text = replace_once(text,
'''        int action = t9Actions[digit];
        t9ActionViews[digit].setText(shortActionName(action));''',
'''        int action = t9Actions[digit];
        t9ActionViews[digit].setText(previewLabel(t9CustomLabels[digit], action));''', "activity t9 preview")
text = replace_once(text,
'''    private String shortActionName(int action) {
        switch (Config.validAction(action)) {''',
'''    private String previewLabel(String configured, int action) {
        if (action == Config.ACTION_NONE) return "—";
        String normalized = Config.normalizeLabelValue(configured);
        if (Config.LABEL_HIDDEN.equals(normalized)) return "隐藏";
        if (!normalized.isEmpty()) return normalized;
        return shortActionName(action);
    }

    private String shortActionName(int action) {
        switch (Config.validAction(action)) {''', "activity preview helper")
text = replace_once(text,
'''            case Config.ACTION_PASTE: return "粘贴";
            case Config.ACTION_DISABLE: return "禁用";''',
'''            case Config.ACTION_PASTE: return "粘贴";
            case Config.ACTION_COPY_ALL: return "全复制";
            case Config.ACTION_CUT_ALL: return "全剪切";
            case Config.ACTION_DISABLE: return "禁用";''', "activity short labels")
path.write_text(text, encoding="utf-8")


# MainHook.java
path = Path("app/src/main/java/com/rww/wetypeswipe/MainHook.java")
text = path.read_text(encoding="utf-8")
text = replace_once(text,
'''            config.copy = intent.getStringExtra(Config.KEY_COPY);
            config.paste = intent.getStringExtra(Config.KEY_PASTE);''',
'''            config.copy = intent.getStringExtra(Config.KEY_COPY);
            config.paste = intent.getStringExtra(Config.KEY_PASTE);
            config.copyAll = intent.getStringExtra(Config.KEY_COPY_ALL);
            config.cutAll = intent.getStringExtra(Config.KEY_CUT_ALL);''', "hook intent actions")
text = replace_once(text,
'''            if (config.paste == null) config.paste = "v";
            if (config.paragraphStart == null) config.paragraphStart = "";''',
'''            if (config.paste == null) config.paste = "v";
            if (config.copyAll == null) config.copyAll = "";
            if (config.cutAll == null) config.cutAll = "";
            if (config.paragraphStart == null) config.paragraphStart = "";''', "hook intent defaults")
text = replace_once(text,
'''            for (int digit = 2; digit <= 9; digit++) {
                config.t9Actions[digit] = Config.validAction(
                        intent.getIntExtra(Config.t9PrefKey(digit), Config.ACTION_NONE));
            }''',
'''            for (char key = 'a'; key <= 'z'; key++) {
                config.qwertyLabels[key - 'a'] = Config.normalizeLabelValue(
                        intent.getStringExtra(Config.qwertyLabelPrefKey(key)));
            }
            for (int digit = 2; digit <= 9; digit++) {
                config.t9Actions[digit] = Config.validAction(
                        intent.getIntExtra(Config.t9PrefKey(digit), Config.ACTION_NONE));
                config.t9Labels[digit] = Config.normalizeLabelValue(
                        intent.getStringExtra(Config.t9LabelPrefKey(digit)));
            }''', "hook intent labels")
text = replace_once(text,
'''                    .putString(Config.KEY_COPY, config.copy)
                    .putString(Config.KEY_PASTE, config.paste)''',
'''                    .putString(Config.KEY_COPY, config.copy)
                    .putString(Config.KEY_PASTE, config.paste)
                    .putString(Config.KEY_COPY_ALL, config.copyAll)
                    .putString(Config.KEY_CUT_ALL, config.cutAll)''', "hook persist actions")
text = replace_once(text,
'''            for (int digit = 2; digit <= 9; digit++) {
                editor.putInt(Config.t9PrefKey(digit), config.t9Actions[digit]);
            }''',
'''            for (char key = 'a'; key <= 'z'; key++) {
                editor.putString(Config.qwertyLabelPrefKey(key),
                        Config.normalizeLabelValue(config.qwertyLabels[key - 'a']));
            }
            for (int digit = 2; digit <= 9; digit++) {
                editor.putInt(Config.t9PrefKey(digit), config.t9Actions[digit]);
                editor.putString(Config.t9LabelPrefKey(digit),
                        Config.normalizeLabelValue(config.t9Labels[digit]));
            }''', "hook persist labels")
text = replace_once(text,
'''            config.copy = prefs.getString(Config.KEY_COPY, "c");
            config.paste = prefs.getString(Config.KEY_PASTE, "v");''',
'''            config.copy = prefs.getString(Config.KEY_COPY, "c");
            config.paste = prefs.getString(Config.KEY_PASTE, "v");
            config.copyAll = prefs.getString(Config.KEY_COPY_ALL, "");
            config.cutAll = prefs.getString(Config.KEY_CUT_ALL, "");''', "hook load actions")
text = replace_once(text,
'''            for (int digit = 2; digit <= 9; digit++) {
                config.t9Actions[digit] = Config.validAction(
                        prefs.getInt(Config.t9PrefKey(digit), Config.ACTION_NONE));
            }''',
'''            for (char key = 'a'; key <= 'z'; key++) {
                config.qwertyLabels[key - 'a'] = Config.normalizeLabelValue(
                        prefs.getString(Config.qwertyLabelPrefKey(key), ""));
            }
            for (int digit = 2; digit <= 9; digit++) {
                config.t9Actions[digit] = Config.validAction(
                        prefs.getInt(Config.t9PrefKey(digit), Config.ACTION_NONE));
                config.t9Labels[digit] = Config.normalizeLabelValue(
                        prefs.getString(Config.t9LabelPrefKey(digit), ""));
            }''', "hook load labels")
text = replace_once(text,
'''                label = action == Config.ACTION_NONE || action == Config.ACTION_DISABLE
                        ? "" : shortActionLabel(action);''',
'''                label = action == Config.ACTION_NONE || action == Config.ACTION_DISABLE
                        ? "" : config.labelFor(key, t9, action);''', "hook native label")
text = replace_once(text,
'''                if (x != null) drawKeyFunctionText(canvas, shortActionLabel(action), x, baseline);''',
'''                if (x != null) drawKeyFunctionText(canvas,
                        config.labelFor(key, false, action), x, baseline);''', "hook qwerty fallback label")
text = replace_once(text,
'''            drawKeyFunctionText(canvas, shortActionLabel(action), item[0], item[1]);''',
'''            drawKeyFunctionText(canvas, config.labelFor(key, t9, action), item[0], item[1]);''', "hook native fallback label")
text = re.sub(r'''    private static String shortActionLabel\(int action\) \{.*?\n    \}\n\n    private static Class<\?> findKeyboardBase''',
'''    private static String shortActionLabel(int action) {
        return Config.shortActionLabel(action);
    }

    private static Class<?> findKeyboardBase''', text, count=1, flags=re.S)
text = replace_once(text,
'''            if (isParagraphAction(action)) {
                success = performParagraphAction(connection, action);
            } else {
                success = performMenuAction(ime, connection, Config.menuIdFor(action));
            }''',
'''            if (isParagraphAction(action)) {
                success = performParagraphAction(connection, action);
            } else if (isCompoundAction(action)) {
                success = performCompoundAction(ime, keyboard, connection, action);
            } else {
                success = performMenuAction(ime, connection, Config.menuIdFor(action));
            }''', "hook compound dispatch")
compound_methods = r'''
    private static boolean isCompoundAction(int action) {
        return action == Config.ACTION_COPY_ALL || action == Config.ACTION_CUT_ALL;
    }

    private boolean performCompoundAction(InputMethodService ime, View keyboard,
                                          InputConnection connection, int action) {
        try {
            try { connection.finishComposingText(); } catch (Throwable ignored) {}
            final EditorSnapshot original = readEditorSnapshot(connection);
            if (original != null && original.left == original.right
                    && original.before.isEmpty() && original.after.isEmpty()) return false;
            if (!performMenuAction(ime, connection, android.R.id.selectAll)) return false;

            keyboard.postDelayed(() -> {
                InputConnection active = null;
                try { active = ime.getCurrentInputConnection(); } catch (Throwable ignored) {}
                if (active == null) return;
                int target = action == Config.ACTION_COPY_ALL ? android.R.id.copy : android.R.id.cut;
                boolean success = performMenuAction(ime, active, target);
                if (!success) {
                    logError(Config.actionName(action) + " failed: target editor rejected action", null);
                }
                if (original != null && (action == Config.ACTION_COPY_ALL || !success)) {
                    try {
                        if (active.setSelection(original.left, original.right)) {
                            currentSelectionStart = original.left;
                            currentSelectionEnd = original.right;
                        }
                    } catch (Throwable ignored) {}
                }
            }, 32L);
            return true;
        } catch (Throwable throwable) {
            logError(Config.actionName(action) + " failed", throwable);
            return false;
        }
    }

'''
text = replace_once(text,
'''    private static boolean isNativePanelAction(int action) {''',
compound_methods + '''    private static boolean isNativePanelAction(int action) {''', "hook compound methods")
text = text.replace('logInfo("v1.11.0 entered target package");',
                    'logInfo("v1.11.1-test1 entered target package");', 1)
path.write_text(text, encoding="utf-8")


# Build version
path = Path("app/build.gradle.kts")
text = path.read_text(encoding="utf-8")
text = re.sub(r'versionCode\s*=\s*\d+', 'versionCode = 39', text, count=1)
text = re.sub(r'versionName\s*=\s*"[^"]+"', 'versionName = "1.11.1-test1"', text, count=1)
path.write_text(text, encoding="utf-8")

print("Applied v1.11.1-test1 full-copy/full-cut/custom-label patch")
