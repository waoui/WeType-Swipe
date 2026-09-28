from pathlib import Path
import re

ROOT = Path('.')

def read(path): return (ROOT/path).read_text(encoding='utf-8')
def write(path,text):
    p=ROOT/path; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text,encoding='utf-8')
def replace(path, old, new, count=1):
    text=read(path)
    if old not in text:
        raise SystemExit(f'pattern not found in {path}: {old[:160]!r}')
    text=text.replace(old,new,count)
    write(path,text)
def sub(path, pattern, repl, count=1, flags=re.S):
    text=read(path); new,n=re.subn(pattern,repl,text,count=count,flags=flags)
    if n!=count: raise SystemExit(f'regex count {n}!={count} in {path}: {pattern[:120]}')
    write(path,new)

# Test version only. Formal publication will consume the next versionCode.
text=read('gradle.properties')
text=re.sub(r'^VERSION_CODE=\d+$','VERSION_CODE=56',text,flags=re.M)
text=re.sub(r'^VERSION_NAME=.*$','VERSION_NAME=1.11.9-test1',text,flags=re.M)
write('gradle.properties',text)

# Config: delegate metadata and QWERTY field mapping to ActionRegistry.
sub('app/src/main/java/com/rww/wetypeswipe/Config.java',
    r'    static final String\[\] ACTION_MENU_LABELS = \{.*?\n    \};\n\n    private static final int\[\] ACTION_MENU_VALUES = \{.*?\n    \};',
    '    static final String[] ACTION_MENU_LABELS = ActionRegistry.menuLabels();')
sub('app/src/main/java/com/rww/wetypeswipe/Config.java',
    r'        bind\(selectAll, ACTION_SELECT_ALL\);.*?        bind\(showInputMethodPicker, ACTION_SHOW_INPUT_METHOD_PICKER\);',
    '        for (int action : ActionRegistry.qwertyActions()) {\n            bind(ActionRegistry.keyFor(this, action), action);\n        }')
sub('app/src/main/java/com/rww/wetypeswipe/Config.java',
    r'    static int validAction\(int action\) \{.*?\n    \}\n\n    static int menuPositionForAction\(int action\) \{.*?\n    \}\n\n    static int actionForMenuPosition\(int position\) \{.*?\n    \}',
    '''    static int validAction(int action) {
        return ActionRegistry.validAction(action);
    }

    static int menuPositionForAction(int action) {
        return ActionRegistry.menuPositionForAction(action);
    }

    static int actionForMenuPosition(int position) {
        return ActionRegistry.actionForMenuPosition(position);
    }''')
sub('app/src/main/java/com/rww/wetypeswipe/Config.java',
    r'    static String shortActionLabel\(int action\) \{.*?\n    \}\n\n    static String t9PrefKey',
    '    static String shortActionLabel(int action) {\n        return ActionRegistry.shortLabel(action);\n    }\n\n    static String t9PrefKey')
sub('app/src/main/java/com/rww/wetypeswipe/Config.java',
    r'    static String actionName\(int action\) \{.*?\n    \}\n\}',
    '    static String actionName(int action) {\n        return ActionRegistry.name(action);\n    }\n}')

# Embedded editor: no duplicated action list or field switch.
sub('app/src/main/java/com/rww/wetypeswipe/EmbeddedConfigEditor.java',
    r'    static final int\[\] QWERTY_ACTIONS = \{.*?\n    \};',
    '    static final int[] QWERTY_ACTIONS = ActionRegistry.qwertyActions();')
sub('app/src/main/java/com/rww/wetypeswipe/EmbeddedConfigEditor.java',
    r'    static String keyForAction\(Config config, int action\) \{.*?\n    \}\n\n    static void setKeyForAction\(Config config, int action, String key\) \{.*?\n    \}',
    '''    static String keyForAction(Config config, int action) {
        return ActionRegistry.keyFor(config, action);
    }

    static void setKeyForAction(Config config, int action, String key) {
        ActionRegistry.setKey(config, action, key);
    }''')

# ConfigSnapshot is now a thin compatibility facade around ConfigCodec.
write('app/src/main/java/com/rww/wetypeswipe/ConfigSnapshot.java', r'''package com.rww.wetypeswipe;

import android.content.Intent;

final class ConfigSnapshot {
    private ConfigSnapshot() {}

    static Config copyOf(Config source) {
        return ConfigCodec.copyOf(source);
    }

    static void putInto(Intent intent, Config config) {
        ConfigCodec.putIntoIntent(intent, config);
    }
}
''')

# MainActivity: registry-backed action metadata + codec-backed load/save/broadcast.
sub('app/src/main/java/com/rww/wetypeswipe/MainActivity.java',
    r'    private static final int\[\] QWERTY_ACTIONS = \{.*?\n    \};\n\n    private static final String\[\] QWERTY_LABELS = \{.*?\n    \};',
    '    private static final int[] QWERTY_ACTIONS = ActionRegistry.qwertyActions();\n    private static final String[] QWERTY_LABELS = ActionRegistry.qwertyLabels();')
sub('app/src/main/java/com/rww/wetypeswipe/MainActivity.java',
    r'    private void loadUiState\(\) \{.*?\n    \}\n\n    private void save\(\) \{',
    '''    private void loadUiState() {
        Config config = ConfigCodec.fromPreferences(prefs);
        for (int i = 0; i < QWERTY_ACTIONS.length; i++) {
            qwertyKeys[i] = normalizedKey(ActionRegistry.keyFor(config, QWERTY_ACTIONS[i]));
        }
        disabledKeys = normalizedKeys(config.disabledKeys);
        System.arraycopy(config.qwertyLabels, 0, qwertyCustomLabels, 0, qwertyCustomLabels.length);
        System.arraycopy(config.qwertyTexts, 0, qwertyInsertTexts, 0, qwertyInsertTexts.length);
        System.arraycopy(config.t9Actions, 0, t9Actions, 0, t9Actions.length);
        System.arraycopy(config.t9Labels, 0, t9CustomLabels, 0, t9CustomLabels.length);
        System.arraycopy(config.t9Texts, 0, t9InsertTexts, 0, t9InsertTexts.length);
    }

    private Config configFromUi(int revision) {
        Config config = new Config();
        for (int i = 0; i < QWERTY_ACTIONS.length; i++) {
            ActionRegistry.setKey(config, QWERTY_ACTIONS[i], qwertyKeys[i]);
        }
        config.disabledKeys = disabledKeys;
        config.thresholdDp = threshold.getProgress() + 6;
        config.t9ThresholdDp = t9Threshold.getProgress() + 10;
        config.vibration = vibration.isChecked();
        config.showKeyLabels = showKeyLabels.isChecked();
        config.showTriggerHint = showTriggerHint.isChecked();
        config.revision = revision;
        System.arraycopy(t9Actions, 0, config.t9Actions, 0, t9Actions.length);
        System.arraycopy(qwertyCustomLabels, 0, config.qwertyLabels, 0, qwertyCustomLabels.length);
        System.arraycopy(t9CustomLabels, 0, config.t9Labels, 0, t9CustomLabels.length);
        System.arraycopy(qwertyInsertTexts, 0, config.qwertyTexts, 0, qwertyInsertTexts.length);
        System.arraycopy(t9InsertTexts, 0, config.t9Texts, 0, t9InsertTexts.length);
        config.rebuildActionMap();
        return config;
    }

    private void save() {''')
sub('app/src/main/java/com/rww/wetypeswipe/MainActivity.java',
    r'        boolean shouldHideIcon = hideIcon\.isChecked\(\);\n        int revision = prefs\.getInt\(Config\.KEY_REVISION, 0\) \+ 1;\n        SharedPreferences\.Editor editor = prefs\.edit\(\).*?        sendBroadcast\(changed\);',
    '''        boolean shouldHideIcon = hideIcon.isChecked();
        int revision = prefs.getInt(Config.KEY_REVISION, 0) + 1;
        Config config = configFromUi(revision);
        SharedPreferences.Editor editor = prefs.edit();
        ConfigCodec.writeToPreferences(editor, config);
        editor.remove("text_start")
                .remove("text_end")
                .putBoolean(Config.KEY_HIDE_ICON, shouldHideIcon);

        if (!editor.commit()) {
            Toast.makeText(this, "配置保存失败", Toast.LENGTH_SHORT).show();
            return;
        }

        Intent changed = new Intent(Config.ACTION_CONFIG_CHANGED);
        changed.setPackage("com.tencent.wetype");
        ConfigSnapshot.putInto(changed, config);
        sendBroadcast(changed);''')
sub('app/src/main/java/com/rww/wetypeswipe/MainActivity.java',
    r'    private String shortActionName\(int action\) \{.*?\n    \}',
    '''    private String shortActionName(int action) {
        if (Config.validAction(action) == Config.ACTION_DISABLE) return "禁用";
        String label = ActionRegistry.shortLabel(action);
        return label.isEmpty() ? "—" : label;
    }''')

# MainHook: use extracted config bridge, compatibility detector and key resolver.
path='app/src/main/java/com/rww/wetypeswipe/MainHook.java'
text=read(path)
text=text.replace('    private static final String LEGACY_KEYBOARD_BASE = "com.tencent.wetype.plugin.hld.keyboard.selfdraw.n";\n','')
text=text.replace('    private static final String WETYPE_4_KEYBOARD_BASE = "com.tencent.wetype.plugin.hld.keyboard.selfdraw.o";\n','')
text=text.replace('    private static final String SELF_DRAW_PREFIX = "com.tencent.wetype.plugin.hld.keyboard.selfdraw.";\n','')
text=text.replace('    private final ConcurrentHashMap<String, Method> methodCache = new ConcurrentHashMap<>();\n','')
text=text.replace('    private volatile Config cachedConfig = defaultConfig();\n','')
text=text.replace('    private volatile boolean receiverRegistered;\n','')
text=text.replace('    private volatile boolean targetCacheLoaded;\n','')
text=text.replace('    private BroadcastReceiver configReceiver;\n','')
text=text.replace('    private final GestureTracker tracker = new GestureTracker();\n',
'''    private final GestureTracker tracker = new GestureTracker();
    private final Reflector reflector = new Reflector();
    private final KeyResolver keyResolver = new KeyResolver(reflector);
    private final ConfigBridge configBridge = new ConfigBridge(TARGET, new ConfigBridge.Listener() {
        @Override public void onConfigChanged(Config config) { nativeSingleKeyLabelCache.clear(); }
        @Override public void info(String message) { logInfo(message); }
        @Override public void error(String message, Throwable throwable) { logError(message, throwable); }
    });
''')
text=re.sub(r'\n    private static Config defaultConfig\(\) \{.*?\n    \}\n', '\n', text, count=1, flags=re.S)
text=text.replace('() -> ConfigSnapshot.copyOf(cachedConfig)', '() -> ConfigSnapshot.copyOf(configBridge.current())')
text=re.sub(r'    private synchronized void applyEmbeddedConfig\(Context context, Config config\) \{.*?\n    \}\n\n    private void captureIme',
'''    private synchronized void applyEmbeddedConfig(Context context, Config config) {
        configBridge.applyEmbedded(context, config);
    }

    private void captureIme''', text, count=1, flags=re.S)
text=re.sub(r'    @SuppressLint\("UnspecifiedRegisterReceiverFlag"\).*?    private static int clamp\(int value, int min, int max, int fallback\) \{\n        return value < min \|\| value > max \? fallback : value;\n    \}\n\n',
'''    private void ensureConfigSync(Context context) {
        configBridge.ensureSync(context);
    }

''', text, count=1, flags=re.S)
text=text.replace('findKeyboardBase(view.getClass())', 'KeyboardCompat.findKeyboardBase(view.getClass())')
text=text.replace('isHandwritingContext(view)', 'KeyboardCompat.isHandwritingContext(view)')
text=text.replace('isHandwritingContext(keyboard)', 'KeyboardCompat.isHandwritingContext(keyboard)')
text=text.replace('!targetCacheLoaded', '!configBridge.isLoaded()')
text=text.replace('cachedConfig', 'configBridge.current()')
text=text.replace('visibleKeyFromButton(model)', 'keyResolver.visibleKeyFromButton(model)')
text=text.replace('keyFromButton(keyboard, button)', 'keyResolver.keyFromButton(keyboard, button)')
text=text.replace('keyAfterDown(keyboard, event)', 'keyResolver.keyAfterDown(keyboard, event)')
text=text.replace('invoke(model, "W")', 'reflector.invoke(model, "W")')
text=text.replace('invoke(model, "t")', 'reflector.invoke(model, "t")')
text=text.replace('invoke(keyboard, "v1", event, false)', 'reflector.invoke(keyboard, "v1", event, false)')
text=text.replace('invoke(keyboard, "v1", event, true)', 'reflector.invoke(keyboard, "v1", event, true)')
text=text.replace('findMethod(', 'Reflector.findMethod(')
text=re.sub(r'    private static Class<\?> findKeyboardBase\(Class<\?> type\) \{.*?\n    private Object interceptKeyboardTouch',
            '    private Object interceptKeyboardTouch', text, count=1, flags=re.S)
text=re.sub(r'    private KeyInfo keyAfterDown\(Object keyboard, MotionEvent event\) \{.*?\n    private void performAction',
            '    private void performAction', text, count=1, flags=re.S)
text=text.replace('isInputMethodAction(action)', 'ActionRegistry.isInputMethodAction(action)')
text=text.replace('isDocumentAction(action)', 'ActionRegistry.isDocumentAction(action)')
text=text.replace('isParagraphAction(action)', 'ActionRegistry.isParagraphAction(action)')
text=text.replace('isCompoundAction(action)', 'ActionRegistry.isCompoundAction(action)')
text=text.replace('isEditorHistoryAction(action)', 'ActionRegistry.isEditorHistoryAction(action)')
text=text.replace('isNativePanelAction(action)', 'ActionRegistry.isNativePanelAction(action)')
for name in ['isInputMethodAction','isCompoundAction','isEditorHistoryAction','isNativePanelAction','isDocumentAction','isParagraphAction']:
    text=re.sub(r'\n    private static boolean '+name+r'\(int action\) \{.*?\n    \}\n', '\n', text, count=1, flags=re.S)
text=re.sub(r'logInfo\("v1\.11\.8(?:-test1)? entered target package; system input-method actions enabled"\);',
            'logInfo("v1.11.9-test1 entered target package; phase-1 architecture refactor enabled");', text)
write(path,text)

# Test-only header labels; no behavior change.
for p in ['app/src/main/java/com/rww/wetypeswipe/MainActivity.java',
          'app/src/main/java/com/rww/wetypeswipe/EmbeddedSettingsUi.java']:
    text=read(p)
    text=re.sub(r'v1\.11\.8(?:-test1)?[^"\n]*', 'v1.11.9-test1 · 架构重构测试', text, count=1)
    write(p,text)

# Clean imports left behind by moving config sync out of MainHook.
for unused in [
    'import android.annotation.SuppressLint;\n',
    'import android.content.BroadcastReceiver;\n',
    'import android.content.Intent;\n',
    'import android.content.IntentFilter;\n',
    'import android.content.SharedPreferences;\n',
]:
    replace('app/src/main/java/com/rww/wetypeswipe/MainHook.java', unused, '', 1)

write('docs/ARCHITECTURE.md', r'''# 模块架构

## 分层

- `MainHook`：只负责 Xposed Hook 编排、手势状态、标签绘制和动作调度。
- `ActionRegistry`：动作 ID、名称、短标签、菜单顺序、26 键存储字段和动作类别的唯一来源。
- `ConfigCodec`：模块配置在 SharedPreferences / Intent / 目标缓存之间的统一序列化。
- `ConfigBridge`：微信输入法进程内的配置广播、缓存和热更新。
- `KeyboardCompat`：微信输入法自绘键盘基类与手写上下文识别。
- `KeyResolver`：将微信输入法内部按键模型解析为稳定的 QWERTY / T9 键值。
- `Reflector`：混淆成员调用的缓存反射工具。
- `ToolbarCarrierLayout`：微信输入法原生剪贴板 / 快捷发送工具栏载体兼容。

## 维护规则

1. 新动作 ID 继续只允许向后追加；动作元数据先登记到 `ActionRegistry`，不要在 UI、Config 和 Hook 中分别复制动作数组/名称。
2. 新配置字段优先进入 `ConfigCodec`，保证模块设置、广播快照和目标缓存一次同步。
3. 微信输入法版本兼容优先落到 `KeyboardCompat`、`KeyResolver` 或专用 Bridge，不再把版本判断堆回 `MainHook`。
4. 重构不得改变动作 ID、默认键位、密码框隔离、手势阈值和已验证的微信输入法兼容语义。
5. 每次新增动作或配置字段都必须补注册完整性/配置往返测试。
''')

text=read('AGENTS.md')
text, changed = re.subn(
    r'8\. 新增动作 ID 只能向后追加，禁止重排已发布动作编号；当前已使用 0[–-](?:20|23)。\n',
    '8. 新增动作 ID 只能向后追加，禁止重排已发布动作编号；当前已使用 0–23。\n'
    '9. 动作元数据统一维护在 `ActionRegistry`，配置序列化统一维护在 `ConfigCodec`；禁止重新在 UI/Hook 中复制整套动作表或配置字段清单。\n',
    text, count=1)
if changed != 1:
    raise SystemExit('AGENTS action-id rule not found')
write('AGENTS.md', text)

print('phase1 source patch applied')
