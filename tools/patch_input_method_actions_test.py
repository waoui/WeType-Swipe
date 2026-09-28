from pathlib import Path


def replace(path, old, new, count=1):
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"pattern not found in {path}: {old[:120]!r}")
    text = text.replace(old, new, count)
    p.write_text(text, encoding="utf-8")


replace("gradle.properties", "VERSION_CODE=53\nVERSION_NAME=1.11.7", "VERSION_CODE=54\nVERSION_NAME=1.11.8-test1")
replace("app/build.gradle.kts", "minSdk = 26", "minSdk = 28")

replace("app/src/main/java/com/rww/wetypeswipe/Config.java",
        '    static final String KEY_REDO = "redo";\n',
        '    static final String KEY_REDO = "redo";\n'
        '    static final String KEY_NEXT_INPUT_METHOD = "next_input_method";\n'
        '    static final String KEY_PREVIOUS_INPUT_METHOD = "previous_input_method";\n'
        '    static final String KEY_SHOW_INPUT_METHOD_PICKER = "show_input_method_picker";\n')
replace("app/src/main/java/com/rww/wetypeswipe/Config.java",
        '    static final int ACTION_INSERT_TEXT = 20;\n',
        '    static final int ACTION_INSERT_TEXT = 20;\n'
        '    static final int ACTION_NEXT_INPUT_METHOD = 21;\n'
        '    static final int ACTION_PREVIOUS_INPUT_METHOD = 22;\n'
        '    static final int ACTION_SHOW_INPUT_METHOD_PICKER = 23;\n')
replace("app/src/main/java/com/rww/wetypeswipe/Config.java",
        '            "剪贴板", "快捷发送", "撤销", "重做", "输入指定内容", "禁用下滑"\n',
        '            "剪贴板", "快捷发送", "撤销", "重做", "输入指定内容",\n'
        '            "下一个输入法", "上一个输入法", "选择输入法", "禁用下滑"\n')
replace("app/src/main/java/com/rww/wetypeswipe/Config.java",
        '            ACTION_REDO,\n            ACTION_INSERT_TEXT,\n            ACTION_DISABLE\n',
        '            ACTION_REDO,\n            ACTION_INSERT_TEXT,\n'
        '            ACTION_NEXT_INPUT_METHOD,\n            ACTION_PREVIOUS_INPUT_METHOD,\n'
        '            ACTION_SHOW_INPUT_METHOD_PICKER,\n            ACTION_DISABLE\n')
replace("app/src/main/java/com/rww/wetypeswipe/Config.java",
        '    String redo = "";\n',
        '    String redo = "";\n'
        '    String nextInputMethod = "";\n'
        '    String previousInputMethod = "";\n'
        '    String showInputMethodPicker = "";\n')
replace("app/src/main/java/com/rww/wetypeswipe/Config.java",
        '        bind(redo, ACTION_REDO);\n',
        '        bind(redo, ACTION_REDO);\n'
        '        bind(nextInputMethod, ACTION_NEXT_INPUT_METHOD);\n'
        '        bind(previousInputMethod, ACTION_PREVIOUS_INPUT_METHOD);\n'
        '        bind(showInputMethodPicker, ACTION_SHOW_INPUT_METHOD_PICKER);\n')
replace("app/src/main/java/com/rww/wetypeswipe/Config.java",
        '        return action >= ACTION_NONE && action <= ACTION_INSERT_TEXT\n',
        '        return action >= ACTION_NONE && action <= ACTION_SHOW_INPUT_METHOD_PICKER\n')
replace("app/src/main/java/com/rww/wetypeswipe/Config.java",
        '            case ACTION_INSERT_TEXT: return "文本";\n',
        '            case ACTION_INSERT_TEXT: return "文本";\n'
        '            case ACTION_NEXT_INPUT_METHOD: return "下个输入";\n'
        '            case ACTION_PREVIOUS_INPUT_METHOD: return "上个输入";\n'
        '            case ACTION_SHOW_INPUT_METHOD_PICKER: return "选输入法";\n')
replace("app/src/main/java/com/rww/wetypeswipe/Config.java",
        '            case ACTION_INSERT_TEXT: return "输入指定内容";\n',
        '            case ACTION_INSERT_TEXT: return "输入指定内容";\n'
        '            case ACTION_NEXT_INPUT_METHOD: return "下一个输入法";\n'
        '            case ACTION_PREVIOUS_INPUT_METHOD: return "上一个输入法";\n'
        '            case ACTION_SHOW_INPUT_METHOD_PICKER: return "选择输入法";\n')

replace("app/src/main/java/com/rww/wetypeswipe/EmbeddedConfigEditor.java",
        '            Config.ACTION_SELECT_TO_DOCUMENT_END\n',
        '            Config.ACTION_SELECT_TO_DOCUMENT_END,\n'
        '            Config.ACTION_NEXT_INPUT_METHOD,\n'
        '            Config.ACTION_PREVIOUS_INPUT_METHOD,\n'
        '            Config.ACTION_SHOW_INPUT_METHOD_PICKER\n')
replace("app/src/main/java/com/rww/wetypeswipe/EmbeddedConfigEditor.java",
        '            case Config.ACTION_SELECT_TO_DOCUMENT_END: return config.selectToDocumentEnd;\n',
        '            case Config.ACTION_SELECT_TO_DOCUMENT_END: return config.selectToDocumentEnd;\n'
        '            case Config.ACTION_NEXT_INPUT_METHOD: return config.nextInputMethod;\n'
        '            case Config.ACTION_PREVIOUS_INPUT_METHOD: return config.previousInputMethod;\n'
        '            case Config.ACTION_SHOW_INPUT_METHOD_PICKER: return config.showInputMethodPicker;\n')
replace("app/src/main/java/com/rww/wetypeswipe/EmbeddedConfigEditor.java",
        '            case Config.ACTION_SELECT_TO_DOCUMENT_END: config.selectToDocumentEnd = value; break;\n',
        '            case Config.ACTION_SELECT_TO_DOCUMENT_END: config.selectToDocumentEnd = value; break;\n'
        '            case Config.ACTION_NEXT_INPUT_METHOD: config.nextInputMethod = value; break;\n'
        '            case Config.ACTION_PREVIOUS_INPUT_METHOD: config.previousInputMethod = value; break;\n'
        '            case Config.ACTION_SHOW_INPUT_METHOD_PICKER: config.showInputMethodPicker = value; break;\n')

replace("app/src/main/java/com/rww/wetypeswipe/ConfigSnapshot.java",
        '        target.redo = source.redo;\n',
        '        target.redo = source.redo;\n'
        '        target.nextInputMethod = source.nextInputMethod;\n'
        '        target.previousInputMethod = source.previousInputMethod;\n'
        '        target.showInputMethodPicker = source.showInputMethodPicker;\n')
replace("app/src/main/java/com/rww/wetypeswipe/ConfigSnapshot.java",
        '        intent.putExtra(Config.KEY_REDO, config.redo);\n',
        '        intent.putExtra(Config.KEY_REDO, config.redo);\n'
        '        intent.putExtra(Config.KEY_NEXT_INPUT_METHOD, config.nextInputMethod);\n'
        '        intent.putExtra(Config.KEY_PREVIOUS_INPUT_METHOD, config.previousInputMethod);\n'
        '        intent.putExtra(Config.KEY_SHOW_INPUT_METHOD_PICKER, config.showInputMethodPicker);\n')

replace("app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
        '            Config.ACTION_SELECT_TO_DOCUMENT_END\n',
        '            Config.ACTION_SELECT_TO_DOCUMENT_END,\n'
        '            Config.ACTION_NEXT_INPUT_METHOD,\n'
        '            Config.ACTION_PREVIOUS_INPUT_METHOD,\n'
        '            Config.ACTION_SHOW_INPUT_METHOD_PICKER\n')
replace("app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
        '            "文首", "文尾", "选至文首", "选至文尾"\n',
        '            "文首", "文尾", "选至文首", "选至文尾",\n'
        '            "下一个输入法", "上一个输入法", "选择输入法"\n')
replace("app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
        '        TextView version = text("v1.11.6 · 新增内置设置与指定内容", 13, COLOR_SECONDARY);\n',
        '        TextView version = text("v1.11.8-test1 · 输入法切换测试", 13, COLOR_SECONDARY);\n')
replace("app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
        '        qwertyKeys[17] = normalizedKey(prefs.getString(Config.KEY_SELECT_TO_DOCUMENT_END, ""));\n',
        '        qwertyKeys[17] = normalizedKey(prefs.getString(Config.KEY_SELECT_TO_DOCUMENT_END, ""));\n'
        '        qwertyKeys[18] = normalizedKey(prefs.getString(Config.KEY_NEXT_INPUT_METHOD, ""));\n'
        '        qwertyKeys[19] = normalizedKey(prefs.getString(Config.KEY_PREVIOUS_INPUT_METHOD, ""));\n'
        '        qwertyKeys[20] = normalizedKey(prefs.getString(Config.KEY_SHOW_INPUT_METHOD_PICKER, ""));\n')
replace("app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
        '                .putString(Config.KEY_SELECT_TO_DOCUMENT_END, qwertyKeys[17])\n',
        '                .putString(Config.KEY_SELECT_TO_DOCUMENT_END, qwertyKeys[17])\n'
        '                .putString(Config.KEY_NEXT_INPUT_METHOD, qwertyKeys[18])\n'
        '                .putString(Config.KEY_PREVIOUS_INPUT_METHOD, qwertyKeys[19])\n'
        '                .putString(Config.KEY_SHOW_INPUT_METHOD_PICKER, qwertyKeys[20])\n')
replace("app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
        '        changed.putExtra(Config.KEY_SELECT_TO_DOCUMENT_END, qwertyKeys[17]);\n',
        '        changed.putExtra(Config.KEY_SELECT_TO_DOCUMENT_END, qwertyKeys[17]);\n'
        '        changed.putExtra(Config.KEY_NEXT_INPUT_METHOD, qwertyKeys[18]);\n'
        '        changed.putExtra(Config.KEY_PREVIOUS_INPUT_METHOD, qwertyKeys[19]);\n'
        '        changed.putExtra(Config.KEY_SHOW_INPUT_METHOD_PICKER, qwertyKeys[20]);\n')
replace("app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
        '            case Config.ACTION_INSERT_TEXT: return "文本";\n',
        '            case Config.ACTION_INSERT_TEXT: return "文本";\n'
        '            case Config.ACTION_NEXT_INPUT_METHOD: return "下个输入";\n'
        '            case Config.ACTION_PREVIOUS_INPUT_METHOD: return "上个输入";\n'
        '            case Config.ACTION_SHOW_INPUT_METHOD_PICKER: return "选输入法";\n')

replace("app/src/main/java/com/rww/wetypeswipe/EmbeddedSettingsUi.java",
        '        TextView version = text(activity, "v1.11.6 · 内置模块模式", 13, SECONDARY);\n',
        '        TextView version = text(activity, "v1.11.8-test1 · 内置模块模式", 13, SECONDARY);\n')

replace("app/src/main/java/com/rww/wetypeswipe/MainHook.java",
        'import android.view.inputmethod.InputConnection;\n',
        'import android.view.inputmethod.InputConnection;\nimport android.view.inputmethod.InputMethodManager;\n')
replace("app/src/main/java/com/rww/wetypeswipe/MainHook.java",
        '            config.redo = intent.getStringExtra(Config.KEY_REDO);\n',
        '            config.redo = intent.getStringExtra(Config.KEY_REDO);\n'
        '            config.nextInputMethod = intent.getStringExtra(Config.KEY_NEXT_INPUT_METHOD);\n'
        '            config.previousInputMethod = intent.getStringExtra(Config.KEY_PREVIOUS_INPUT_METHOD);\n'
        '            config.showInputMethodPicker = intent.getStringExtra(Config.KEY_SHOW_INPUT_METHOD_PICKER);\n')
replace("app/src/main/java/com/rww/wetypeswipe/MainHook.java",
        '            if (config.redo == null) config.redo = "";\n',
        '            if (config.redo == null) config.redo = "";\n'
        '            if (config.nextInputMethod == null) config.nextInputMethod = "";\n'
        '            if (config.previousInputMethod == null) config.previousInputMethod = "";\n'
        '            if (config.showInputMethodPicker == null) config.showInputMethodPicker = "";\n')
replace("app/src/main/java/com/rww/wetypeswipe/MainHook.java",
        '                    .putString(Config.KEY_REDO, config.redo)\n',
        '                    .putString(Config.KEY_REDO, config.redo)\n'
        '                    .putString(Config.KEY_NEXT_INPUT_METHOD, config.nextInputMethod)\n'
        '                    .putString(Config.KEY_PREVIOUS_INPUT_METHOD, config.previousInputMethod)\n'
        '                    .putString(Config.KEY_SHOW_INPUT_METHOD_PICKER, config.showInputMethodPicker)\n')
replace("app/src/main/java/com/rww/wetypeswipe/MainHook.java",
        '            config.redo = prefs.getString(Config.KEY_REDO, "");\n',
        '            config.redo = prefs.getString(Config.KEY_REDO, "");\n'
        '            config.nextInputMethod = prefs.getString(Config.KEY_NEXT_INPUT_METHOD, "");\n'
        '            config.previousInputMethod = prefs.getString(Config.KEY_PREVIOUS_INPUT_METHOD, "");\n'
        '            config.showInputMethodPicker = prefs.getString(Config.KEY_SHOW_INPUT_METHOD_PICKER, "");\n')
replace("app/src/main/java/com/rww/wetypeswipe/MainHook.java",
        '            EditorInfo editorInfo = ime.getCurrentInputEditorInfo();\n            if (editorInfo != null && isPassword(editorInfo.inputType)) return;\n\n            if (isNativePanelAction(action)) {\n',
        '            if (isInputMethodAction(action)) {\n'
        '                hideKeyboardHint(0L);\n'
        '                if (!performInputMethodAction(ime, action)) {\n'
        '                    logError(actionName + " failed: system rejected input-method action", null);\n'
        '                }\n'
        '                return;\n'
        '            }\n\n'
        '            EditorInfo editorInfo = ime.getCurrentInputEditorInfo();\n'
        '            if (editorInfo != null && isPassword(editorInfo.inputType)) return;\n\n'
        '            if (isNativePanelAction(action)) {\n')
replace("app/src/main/java/com/rww/wetypeswipe/MainHook.java",
        '    private boolean performInsertText(InputConnection connection, String text) {\n',
        '    private static boolean isInputMethodAction(int action) {\n'
        '        return action == Config.ACTION_NEXT_INPUT_METHOD\n'
        '                || action == Config.ACTION_PREVIOUS_INPUT_METHOD\n'
        '                || action == Config.ACTION_SHOW_INPUT_METHOD_PICKER;\n'
        '    }\n\n'
        '    private boolean performInputMethodAction(InputMethodService ime, int action) {\n'
        '        if (ime == null) return false;\n'
        '        if (action == Config.ACTION_NEXT_INPUT_METHOD) return ime.switchToNextInputMethod(false);\n'
        '        if (action == Config.ACTION_PREVIOUS_INPUT_METHOD) return ime.switchToPreviousInputMethod();\n'
        '        if (action == Config.ACTION_SHOW_INPUT_METHOD_PICKER) {\n'
        '            Object service = ime.getSystemService(Context.INPUT_METHOD_SERVICE);\n'
        '            if (!(service instanceof InputMethodManager)) return false;\n'
        '            ((InputMethodManager) service).showInputMethodPicker();\n'
        '            return true;\n'
        '        }\n'
        '        return false;\n'
        '    }\n\n'
        '    private boolean performInsertText(InputConnection connection, String text) {\n')
replace("app/src/main/java/com/rww/wetypeswipe/MainHook.java",
        '            logInfo("v1.11.7 entered target package; WeType 4.0.0 keyboard and native-panel compatibility enabled");\n',
        '            logInfo("v1.11.8-test1 entered target package; system input-method actions enabled");\n')

Path("app/src/test/java/com/rww/wetypeswipe/InputMethodActionTest.java").write_text('''package com.rww.wetypeswipe;\n\nimport static org.junit.Assert.assertEquals;\n\nimport org.junit.Test;\n\npublic class InputMethodActionTest {\n    @Test public void actionIdsAppendWithoutRenumbering() {\n        assertEquals(20, Config.ACTION_INSERT_TEXT);\n        assertEquals(21, Config.ACTION_NEXT_INPUT_METHOD);\n        assertEquals(22, Config.ACTION_PREVIOUS_INPUT_METHOD);\n        assertEquals(23, Config.ACTION_SHOW_INPUT_METHOD_PICKER);\n    }\n\n    @Test public void qwertyInputMethodActionsRoundTrip() {\n        Config config = new Config();\n        EmbeddedConfigEditor.assignQwerty(config, "q", Config.ACTION_NEXT_INPUT_METHOD);\n        EmbeddedConfigEditor.assignQwerty(config, "w", Config.ACTION_PREVIOUS_INPUT_METHOD);\n        EmbeddedConfigEditor.assignQwerty(config, "e", Config.ACTION_SHOW_INPUT_METHOD_PICKER);\n        assertEquals(Config.ACTION_NEXT_INPUT_METHOD, config.actionFor("q", false));\n        assertEquals(Config.ACTION_PREVIOUS_INPUT_METHOD, config.actionFor("w", false));\n        assertEquals(Config.ACTION_SHOW_INPUT_METHOD_PICKER, config.actionFor("e", false));\n    }\n\n    @Test public void t9InputMethodActionsRemainValid() {\n        Config config = new Config();\n        config.t9Actions[2] = Config.ACTION_NEXT_INPUT_METHOD;\n        config.t9Actions[3] = Config.ACTION_PREVIOUS_INPUT_METHOD;\n        config.t9Actions[4] = Config.ACTION_SHOW_INPUT_METHOD_PICKER;\n        config.rebuildActionMap();\n        assertEquals(Config.ACTION_NEXT_INPUT_METHOD, config.actionFor("2", true));\n        assertEquals(Config.ACTION_PREVIOUS_INPUT_METHOD, config.actionFor("3", true));\n        assertEquals(Config.ACTION_SHOW_INPUT_METHOD_PICKER, config.actionFor("4", true));\n    }\n}\n''', encoding="utf-8")

assert "minSdk = 28" in Path("app/build.gradle.kts").read_text(encoding="utf-8")
assert "VERSION_CODE=54" in Path("gradle.properties").read_text(encoding="utf-8")
assert "ACTION_SHOW_INPUT_METHOD_PICKER = 23" in Path("app/src/main/java/com/rww/wetypeswipe/Config.java").read_text(encoding="utf-8")
assert "switchToNextInputMethod(false)" in Path("app/src/main/java/com/rww/wetypeswipe/MainHook.java").read_text(encoding="utf-8")
assert "showInputMethodPicker()" in Path("app/src/main/java/com/rww/wetypeswipe/MainHook.java").read_text(encoding="utf-8")
