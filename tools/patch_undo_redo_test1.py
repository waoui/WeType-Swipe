from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_one(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)


def update(path: str, replacements: list[tuple[str, str, str]]) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    for old, new, label in replacements:
        text = replace_one(text, old, new, f"{path}: {label}")
    target.write_text(text, encoding="utf-8")


update(
    "app/src/main/java/com/rww/wetypeswipe/Config.java",
    [
        (
            '    static final String KEY_OPEN_QUICK_PHRASE = "open_quick_phrase";\n'
            '    static final String KEY_DISABLED_KEYS = "disabled_keys";',
            '    static final String KEY_OPEN_QUICK_PHRASE = "open_quick_phrase";\n'
            '    static final String KEY_UNDO = "undo";\n'
            '    static final String KEY_REDO = "redo";\n'
            '    static final String KEY_DISABLED_KEYS = "disabled_keys";',
            "preference keys",
        ),
        (
            '    static final int ACTION_COPY_ALL = 12;\n'
            '    static final int ACTION_CUT_ALL = 13;',
            '    static final int ACTION_COPY_ALL = 12;\n'
            '    static final int ACTION_CUT_ALL = 13;\n'
            '    static final int ACTION_UNDO = 14;\n'
            '    static final int ACTION_REDO = 15;',
            "action ids",
        ),
        (
            '            "段首", "段尾", "选至段首", "选至段尾",\n'
            '            "剪贴板", "快捷发送", "禁用下滑"',
            '            "段首", "段尾", "选至段首", "选至段尾",\n'
            '            "剪贴板", "快捷发送", "撤销", "重做", "禁用下滑"',
            "menu labels",
        ),
        (
            '            ACTION_OPEN_CLIPBOARD,\n'
            '            ACTION_OPEN_QUICK_PHRASE,\n'
            '            ACTION_DISABLE',
            '            ACTION_OPEN_CLIPBOARD,\n'
            '            ACTION_OPEN_QUICK_PHRASE,\n'
            '            ACTION_UNDO,\n'
            '            ACTION_REDO,\n'
            '            ACTION_DISABLE',
            "menu values",
        ),
        (
            '    String openClipboard = "";\n'
            '    String openQuickPhrase = "";\n'
            '    String disabledKeys = "";',
            '    String openClipboard = "";\n'
            '    String openQuickPhrase = "";\n'
            '    String undo = "";\n'
            '    String redo = "";\n'
            '    String disabledKeys = "";',
            "config fields",
        ),
        (
            '        bind(openClipboard, ACTION_OPEN_CLIPBOARD);\n'
            '        bind(openQuickPhrase, ACTION_OPEN_QUICK_PHRASE);\n'
            '        bindDisabled(disabledKeys);',
            '        bind(openClipboard, ACTION_OPEN_CLIPBOARD);\n'
            '        bind(openQuickPhrase, ACTION_OPEN_QUICK_PHRASE);\n'
            '        bind(undo, ACTION_UNDO);\n'
            '        bind(redo, ACTION_REDO);\n'
            '        bindDisabled(disabledKeys);',
            "action map",
        ),
        (
            '        return action >= ACTION_NONE && action <= ACTION_CUT_ALL\n'
            '                ? action : ACTION_NONE;',
            '        return action >= ACTION_NONE && action <= ACTION_REDO\n'
            '                ? action : ACTION_NONE;',
            "valid action range",
        ),
        (
            '            case ACTION_OPEN_CLIPBOARD: return "剪贴";\n'
            '            case ACTION_OPEN_QUICK_PHRASE: return "快捷";\n'
            '            default: return "";',
            '            case ACTION_OPEN_CLIPBOARD: return "剪贴";\n'
            '            case ACTION_OPEN_QUICK_PHRASE: return "快捷";\n'
            '            case ACTION_UNDO: return "撤销";\n'
            '            case ACTION_REDO: return "重做";\n'
            '            default: return "";',
            "short labels",
        ),
        (
            '        if (action == ACTION_PASTE) return android.R.id.paste;\n'
            '        return 0;',
            '        if (action == ACTION_PASTE) return android.R.id.paste;\n'
            '        if (action == ACTION_UNDO) return android.R.id.undo;\n'
            '        if (action == ACTION_REDO) return android.R.id.redo;\n'
            '        return 0;',
            "menu ids",
        ),
        (
            '            case ACTION_OPEN_CLIPBOARD: return "剪贴板";\n'
            '            case ACTION_OPEN_QUICK_PHRASE: return "快捷发送";\n'
            '            default: return "未绑定";',
            '            case ACTION_OPEN_CLIPBOARD: return "剪贴板";\n'
            '            case ACTION_OPEN_QUICK_PHRASE: return "快捷发送";\n'
            '            case ACTION_UNDO: return "撤销";\n'
            '            case ACTION_REDO: return "重做";\n'
            '            default: return "未绑定";',
            "action names",
        ),
    ],
)

update(
    "app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
    [
        (
            '            Config.ACTION_OPEN_CLIPBOARD,\n'
            '            Config.ACTION_OPEN_QUICK_PHRASE\n'
            '    };',
            '            Config.ACTION_OPEN_CLIPBOARD,\n'
            '            Config.ACTION_OPEN_QUICK_PHRASE,\n'
            '            Config.ACTION_UNDO,\n'
            '            Config.ACTION_REDO\n'
            '    };',
            "qwerty action list",
        ),
        (
            '            "段首", "段尾", "选至段首", "选至段尾",\n'
            '            "剪贴板", "快捷发送"\n'
            '    };',
            '            "段首", "段尾", "选至段首", "选至段尾",\n'
            '            "剪贴板", "快捷发送", "撤销", "重做"\n'
            '    };',
            "qwerty labels",
        ),
        (
            '        TextView version = text("v1.11.3 · 修复原生面板与符号页标签", 13, COLOR_SECONDARY);',
            '        TextView version = text("v1.11.4-test1 · 新增撤销与重做", 13, COLOR_SECONDARY);',
            "version header",
        ),
        (
            '        qwertyKeys[10] = normalizedKey(prefs.getString(Config.KEY_OPEN_CLIPBOARD, ""));\n'
            '        qwertyKeys[11] = normalizedKey(prefs.getString(Config.KEY_OPEN_QUICK_PHRASE, ""));\n'
            '        disabledKeys = normalizedKeys(prefs.getString(Config.KEY_DISABLED_KEYS, ""));',
            '        qwertyKeys[10] = normalizedKey(prefs.getString(Config.KEY_OPEN_CLIPBOARD, ""));\n'
            '        qwertyKeys[11] = normalizedKey(prefs.getString(Config.KEY_OPEN_QUICK_PHRASE, ""));\n'
            '        qwertyKeys[12] = normalizedKey(prefs.getString(Config.KEY_UNDO, ""));\n'
            '        qwertyKeys[13] = normalizedKey(prefs.getString(Config.KEY_REDO, ""));\n'
            '        disabledKeys = normalizedKeys(prefs.getString(Config.KEY_DISABLED_KEYS, ""));',
            "load mappings",
        ),
        (
            '                .putString(Config.KEY_OPEN_CLIPBOARD, qwertyKeys[10])\n'
            '                .putString(Config.KEY_OPEN_QUICK_PHRASE, qwertyKeys[11])\n'
            '                .putString(Config.KEY_DISABLED_KEYS, disabledKeys)',
            '                .putString(Config.KEY_OPEN_CLIPBOARD, qwertyKeys[10])\n'
            '                .putString(Config.KEY_OPEN_QUICK_PHRASE, qwertyKeys[11])\n'
            '                .putString(Config.KEY_UNDO, qwertyKeys[12])\n'
            '                .putString(Config.KEY_REDO, qwertyKeys[13])\n'
            '                .putString(Config.KEY_DISABLED_KEYS, disabledKeys)',
            "persist mappings",
        ),
        (
            '        changed.putExtra(Config.KEY_OPEN_CLIPBOARD, qwertyKeys[10]);\n'
            '        changed.putExtra(Config.KEY_OPEN_QUICK_PHRASE, qwertyKeys[11]);\n'
            '        changed.putExtra(Config.KEY_DISABLED_KEYS, disabledKeys);',
            '        changed.putExtra(Config.KEY_OPEN_CLIPBOARD, qwertyKeys[10]);\n'
            '        changed.putExtra(Config.KEY_OPEN_QUICK_PHRASE, qwertyKeys[11]);\n'
            '        changed.putExtra(Config.KEY_UNDO, qwertyKeys[12]);\n'
            '        changed.putExtra(Config.KEY_REDO, qwertyKeys[13]);\n'
            '        changed.putExtra(Config.KEY_DISABLED_KEYS, disabledKeys);',
            "broadcast mappings",
        ),
        (
            '            case Config.ACTION_OPEN_CLIPBOARD: return "剪贴板";\n'
            '            case Config.ACTION_OPEN_QUICK_PHRASE: return "快捷语";\n'
            '            default: return "—";',
            '            case Config.ACTION_OPEN_CLIPBOARD: return "剪贴板";\n'
            '            case Config.ACTION_OPEN_QUICK_PHRASE: return "快捷语";\n'
            '            case Config.ACTION_UNDO: return "撤销";\n'
            '            case Config.ACTION_REDO: return "重做";\n'
            '            default: return "—";',
            "preview names",
        ),
    ],
)

update(
    "app/src/main/java/com/rww/wetypeswipe/MainHook.java",
    [
        (
            '            logInfo("v1.11.3 entered target package; native-panel structural adapter enabled");',
            '            logInfo("v1.11.4-test1 entered target package; undo/redo actions enabled");',
            "runtime version log",
        ),
        (
            '            config.openClipboard = intent.getStringExtra(Config.KEY_OPEN_CLIPBOARD);\n'
            '            config.openQuickPhrase = intent.getStringExtra(Config.KEY_OPEN_QUICK_PHRASE);\n'
            '            config.disabledKeys = intent.getStringExtra(Config.KEY_DISABLED_KEYS);',
            '            config.openClipboard = intent.getStringExtra(Config.KEY_OPEN_CLIPBOARD);\n'
            '            config.openQuickPhrase = intent.getStringExtra(Config.KEY_OPEN_QUICK_PHRASE);\n'
            '            config.undo = intent.getStringExtra(Config.KEY_UNDO);\n'
            '            config.redo = intent.getStringExtra(Config.KEY_REDO);\n'
            '            config.disabledKeys = intent.getStringExtra(Config.KEY_DISABLED_KEYS);',
            "intent mappings",
        ),
        (
            '            if (config.openClipboard == null) config.openClipboard = "";\n'
            '            if (config.openQuickPhrase == null) config.openQuickPhrase = "";\n'
            '            if (config.disabledKeys == null) config.disabledKeys = "";',
            '            if (config.openClipboard == null) config.openClipboard = "";\n'
            '            if (config.openQuickPhrase == null) config.openQuickPhrase = "";\n'
            '            if (config.undo == null) config.undo = "";\n'
            '            if (config.redo == null) config.redo = "";\n'
            '            if (config.disabledKeys == null) config.disabledKeys = "";',
            "intent defaults",
        ),
        (
            '                    .putString(Config.KEY_OPEN_CLIPBOARD, config.openClipboard)\n'
            '                    .putString(Config.KEY_OPEN_QUICK_PHRASE, config.openQuickPhrase)\n'
            '                    .putString(Config.KEY_DISABLED_KEYS, config.disabledKeys)',
            '                    .putString(Config.KEY_OPEN_CLIPBOARD, config.openClipboard)\n'
            '                    .putString(Config.KEY_OPEN_QUICK_PHRASE, config.openQuickPhrase)\n'
            '                    .putString(Config.KEY_UNDO, config.undo)\n'
            '                    .putString(Config.KEY_REDO, config.redo)\n'
            '                    .putString(Config.KEY_DISABLED_KEYS, config.disabledKeys)',
            "target cache write",
        ),
        (
            '            config.openClipboard = prefs.getString(Config.KEY_OPEN_CLIPBOARD, "");\n'
            '            config.openQuickPhrase = prefs.getString(Config.KEY_OPEN_QUICK_PHRASE, "");\n'
            '            config.disabledKeys = prefs.getString(Config.KEY_DISABLED_KEYS, "");',
            '            config.openClipboard = prefs.getString(Config.KEY_OPEN_CLIPBOARD, "");\n'
            '            config.openQuickPhrase = prefs.getString(Config.KEY_OPEN_QUICK_PHRASE, "");\n'
            '            config.undo = prefs.getString(Config.KEY_UNDO, "");\n'
            '            config.redo = prefs.getString(Config.KEY_REDO, "");\n'
            '            config.disabledKeys = prefs.getString(Config.KEY_DISABLED_KEYS, "");',
            "target cache read",
        ),
        (
            '            if (isParagraphAction(action)) {\n'
            '                success = performParagraphAction(connection, action);\n'
            '            } else if (isCompoundAction(action)) {\n'
            '                success = performCompoundAction(ime, keyboard, connection, action);\n'
            '            } else {\n'
            '                success = performMenuAction(ime, connection, Config.menuIdFor(action));\n'
            '            }',
            '            if (isParagraphAction(action)) {\n'
            '                success = performParagraphAction(connection, action);\n'
            '            } else if (isCompoundAction(action)) {\n'
            '                success = performCompoundAction(ime, keyboard, connection, action);\n'
            '            } else if (isEditorHistoryAction(action)) {\n'
            '                success = performEditorHistoryAction(ime, connection, action);\n'
            '            } else {\n'
            '                success = performMenuAction(ime, connection, Config.menuIdFor(action));\n'
            '            }',
            "action dispatch",
        ),
        (
            '    private static boolean isCompoundAction(int action) {\n'
            '        return action == Config.ACTION_COPY_ALL || action == Config.ACTION_CUT_ALL;\n'
            '    }\n'
            '\n'
            '    private boolean performCompoundAction',
            '    private static boolean isCompoundAction(int action) {\n'
            '        return action == Config.ACTION_COPY_ALL || action == Config.ACTION_CUT_ALL;\n'
            '    }\n'
            '\n'
            '    private static boolean isEditorHistoryAction(int action) {\n'
            '        return action == Config.ACTION_UNDO || action == Config.ACTION_REDO;\n'
            '    }\n'
            '\n'
            '    private boolean performEditorHistoryAction(InputMethodService ime,\n'
            '                                               InputConnection connection, int action) {\n'
            '        try { connection.finishComposingText(); } catch (Throwable ignored) {}\n'
            '        return performMenuAction(ime, connection, Config.menuIdFor(action));\n'
            '    }\n'
            '\n'
            '    private boolean performCompoundAction',
            "history action helper",
        ),
    ],
)

update(
    "app/src/test/java/com/rww/wetypeswipe/ConfigTest.java",
    [
        (
            '    @Test public void labelNormalizationIsUnicodeSafe() {',
            '    @Test public void undoAndRedoRemainBindableAndUseAndroidMenuIds() {\n'
            '        Config config = new Config();\n'
            '        config.undo = "u";\n'
            '        config.redo = "r";\n'
            '        config.rebuildActionMap();\n'
            '\n'
            '        assertEquals(Config.ACTION_UNDO, config.actionFor("u", false));\n'
            '        assertEquals(Config.ACTION_REDO, config.actionFor("r", false));\n'
            '        assertEquals(android.R.id.undo, Config.menuIdFor(Config.ACTION_UNDO));\n'
            '        assertEquals(android.R.id.redo, Config.menuIdFor(Config.ACTION_REDO));\n'
            '        assertEquals("撤销", Config.shortActionLabel(Config.ACTION_UNDO));\n'
            '        assertEquals("重做", Config.actionName(Config.ACTION_REDO));\n'
            '    }\n'
            '\n'
            '    @Test public void labelNormalizationIsUnicodeSafe() {',
            "undo redo unit test",
        ),
    ],
)

update(
    "gradle.properties",
    [
        (
            'VERSION_CODE=41\nVERSION_NAME=1.11.3',
            'VERSION_CODE=42\nVERSION_NAME=1.11.4-test1',
            "test version",
        ),
    ],
)

notes = """# 微信输入法下滑快捷键 v1.11.4-test1

## 新增功能

- 26 键和九宫格均可绑定“撤销”和“重做”。
- 下滑触发后优先结束当前中文组词状态，再向目标输入框发送 Android 标准撤销／重做菜单指令。
- 不自行保存输入内容或维护私有撤销栈，避免跨应用文本泄露和状态冲突。

## 兼容性说明

撤销／重做依赖目标 App 的编辑器实现。标准 Android 文本框通常可用；WPS、富文本网页、小程序或自绘编辑器可能拒绝该指令。目标编辑器没有历史记录时应无变化，不应崩溃或误删内容。

## 真机验收

1. 在模块设置中分别为两个按键绑定“撤销”和“重做”，保存后标签正确显示。
2. 微信聊天输入框连续输入多段文字，撤销后最近一次编辑被回退，重做后恢复。
3. 测试中文候选词上屏、删除、粘贴、剪切后的撤销与重做。
4. 测试浏览器普通文本框，以及 WPS 或其他自定义编辑器，记录是否支持。
5. 没有可撤销／重做记录时，不崩溃、不误删内容。
6. 手写找字、数字／符号页面、密码框继续不触发模块动作。
7. 原生剪贴板、快捷发送／常用语和既有下滑功能没有回归。

## 自动验证

- Config 动作编号与历史配置兼容。
- 菜单位置映射可往返。
- 撤销／重做映射至 `android.R.id.undo` 和 `android.R.id.redo`。
- 单元测试、Android Lint、Debug/Release 构建和永久签名校验必须通过。
"""
(ROOT / "TEST_NOTES_v1.11.4-test1.md").write_text(notes, encoding="utf-8")
