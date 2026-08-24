#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


main_hook = ROOT / "app/src/main/java/com/rww/wetypeswipe/MainHook.java"

replace_once(
    main_hook,
    'logInfo("v1.11.2 entered target package; WeType 3.5.0/3.5.2 adapters enabled");',
    'logInfo("v1.11.3-test1 entered target package; native-panel structural adapter enabled");',
)

old_label_block = '''        String label = nativeSingleKeyLabelCache.get(model);
        if (label == null) {
            Config config = cachedConfig;
            if (config == null || !config.hasAnyBinding() || !config.showKeyLabels) return;
            String id;
            try { id = String.valueOf(model); }
            catch (Throwable ignored) { id = null; }
            String key = keyFromNativeLayoutId(id);
            if (key == null) {
                Object value = invoke(model, "K");
                key = keyFromNativeLayoutId(value == null ? null : String.valueOf(value));
            }
            if (key == null) label = "";
            else {
                char value = key.charAt(0);
                boolean t9 = value >= '1' && value <= '9';
                int action = config.actionFor(key, t9);
                label = action == Config.ACTION_NONE || action == Config.ACTION_DISABLE
                        ? "" : config.labelFor(key, t9, action);
            }
            if (nativeSingleKeyLabelCache.size() >= NATIVE_SINGLE_KEY_LABEL_CACHE_LIMIT) {
                nativeSingleKeyLabelCache.clear();
            }
            nativeSingleKeyLabelCache.put(model, label);
        }
        if (label.isEmpty()) return;
'''

new_label_block = '''        Config config = cachedConfig;
        if (config == null || !config.hasAnyBinding() || !config.showKeyLabels) return;

        // Native key models are reused when switching to number/symbol pages. Their layout id
        // still points at the original QWERTY position, so using that id alone leaks labels onto
        // symbol keys. Resolve the currently visible key text and include it in the cache value.
        KeyInfo visibleKey = visibleKeyFromButton(model);
        if (visibleKey == null) {
            nativeSingleKeyLabelCache.remove(model);
            return;
        }
        String identity = (visibleKey.t9 ? "t9:" : "qwerty:") + visibleKey.key + '\\u0000';
        String cached = nativeSingleKeyLabelCache.get(model);
        String label;
        if (cached == null || !cached.startsWith(identity)) {
            int action = config.actionFor(visibleKey.key, visibleKey.t9);
            label = action == Config.ACTION_NONE || action == Config.ACTION_DISABLE
                    ? "" : config.labelFor(visibleKey.key, visibleKey.t9, action);
            if (nativeSingleKeyLabelCache.size() >= NATIVE_SINGLE_KEY_LABEL_CACHE_LIMIT) {
                nativeSingleKeyLabelCache.clear();
            }
            nativeSingleKeyLabelCache.put(model, identity + label);
        } else {
            label = cached.substring(identity.length());
        }
        if (label.isEmpty()) return;
'''
replace_once(main_hook, old_label_block, new_label_block)

old_key_from_button = '''    private KeyInfo keyFromButton(Object keyboard, Object button) {
'''
new_key_from_button = '''    private KeyInfo visibleKeyFromButton(Object button) {
        if (button == null) return null;
        Object keyData = invoke(button, "O");
        if (keyData == null) return null;
        Object main = invoke(keyData, "getMainText");
        Object secondary = firstNonNull(
                invoke(keyData, "getSubText"),
                invoke(keyData, "getSecondaryText"),
                invoke(keyData, "getHintText"),
                invoke(keyData, "getAssistText"));
        return keyFromTexts(main, secondary);
    }

    private KeyInfo keyFromButton(Object keyboard, Object button) {
'''
replace_once(main_hook, old_key_from_button, new_key_from_button)

old_carrier = '''    private Object[] findToolbarCommandCarrier(View view) {
        if (view == null) return null;
        try {
            if (view.hasOnClickListeners() || view.isClickable()) {
                View.OnClickListener listener = readOnClickListener(view);
                String listenerClass = listener == null ? "" : listener.getClass().getName();
                boolean supportedListener = "com.tencent.wetype.plugin.hld.utils.h3".equals(listenerClass)
                        || "com.tencent.wetype.plugin.hld.utils.o1".equals(listenerClass);
                if (listener != null && supportedListener) {
                    Object callback = readNamedField(listener, "c");
                    String callbackClass = callback == null ? "" : callback.getClass().getName();
                    boolean supportedCallback = "com.tencent.wetype.plugin.hld.toolbar.a0$b".equals(callbackClass)
                            || "com.tencent.wetype.plugin.hld.toolbar.A$b".equals(callbackClass);
                    if (callback != null && supportedCallback
                            && readNamedField(callback, "this$0") != null) {
                        logInfo("toolbar carrier matched listener=" + listenerClass
                                + " callback=" + callbackClass);
                        return new Object[]{view, listener, callback};
                    }
                }
            }
        } catch (Throwable ignored) {}
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int index = 0; index < group.getChildCount(); index++) {
                Object[] result = findToolbarCommandCarrier(group.getChildAt(index));
                if (result != null) return result;
            }
        }
        return null;
    }
'''

new_carrier = '''    private Object[] findToolbarCommandCarrier(View view) {
        if (view == null) return null;
        try {
            if (view.hasOnClickListeners() || view.isClickable()) {
                View.OnClickListener listener = readOnClickListener(view);
                Object callback = findToolbarCallback(listener);
                if (callback != null) {
                    logInfo("toolbar carrier matched listener=" + listener.getClass().getName()
                            + " callback=" + callback.getClass().getName());
                    return new Object[]{view, listener, callback};
                }
            }
        } catch (Throwable ignored) {}
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int index = 0; index < group.getChildCount(); index++) {
                Object[] result = findToolbarCommandCarrier(group.getChildAt(index));
                if (result != null) return result;
            }
        }
        return null;
    }

    private Object findToolbarCallback(Object listener) {
        if (listener == null) return null;

        // Fast path for known WeType builds: 3.5.0 uses h3 and the uploaded 3.5.2
        // build uses p1. Both carry the Kotlin callback in field c.
        Object named = readNamedField(listener, "c");
        if (isToolbarCallbackCarrier(named)) return named;

        // Obfuscated wrapper class and field names can change between builds with the same
        // version name. Fall back to structure instead of another single class-name allowlist.
        for (Class<?> type = listener.getClass(); type != null; type = type.getSuperclass()) {
            Field[] fields;
            try { fields = type.getDeclaredFields(); }
            catch (Throwable ignored) { continue; }
            for (Field field : fields) {
                try {
                    if (java.lang.reflect.Modifier.isStatic(field.getModifiers())) continue;
                    field.setAccessible(true);
                    Object candidate = field.get(listener);
                    if (isToolbarCallbackCarrier(candidate)) return candidate;
                } catch (Throwable ignored) {
                }
            }
        }
        return null;
    }

    private boolean isToolbarCallbackCarrier(Object callback) {
        if (callback == null) return false;
        Object holder = readNamedField(callback, "this$0");
        if (holder == null) return false;
        String holderClass = holder.getClass().getName();
        if (!holderClass.startsWith("com.tencent.wetype.plugin.hld.toolbar.")) return false;

        Field function = findNamedField(holder.getClass(), "f");
        Field category = findNamedField(holder.getClass(), "g");
        Field group = findNamedField(holder.getClass(), "h");
        return function != null && function.getType() == int.class
                && category != null
                && group != null && group.getType() == int.class
                && findCompatibleInvoke(callback.getClass()) != null;
    }
'''
replace_once(main_hook, old_carrier, new_carrier)

main_activity = ROOT / "app/src/main/java/com/rww/wetypeswipe/MainActivity.java"
replace_once(
    main_activity,
    'v1.11.2 · 兼容微信输入法 3.5.2',
    'v1.11.3-test1 · 修复原生面板与符号页标签',
)

gradle_properties = ROOT / "gradle.properties"
properties = gradle_properties.read_text(encoding="utf-8")
properties, code_count = re.subn(r"(?m)^VERSION_CODE=.*$", "VERSION_CODE=41", properties, count=1)
properties, name_count = re.subn(r"(?m)^VERSION_NAME=.*$", "VERSION_NAME=1.11.3-test1", properties, count=1)
if code_count != 1 or name_count != 1:
    raise SystemExit("Could not update VERSION_CODE/VERSION_NAME")
gradle_properties.write_text(properties, encoding="utf-8")

notes = ROOT / "TEST_NOTES_v1.11.3-test1.md"
notes.write_text("""# 微信输入法下滑快捷键 v1.11.3-test1

## 修复内容

- 修复上传的微信输入法 3.5.2 APK 中原生剪贴板、快捷发送／常用语入口失效。
- 不再把工具栏监听器写死为单一混淆类名，改为“已知字段快速匹配 + 结构特征回退”。
- 修复数字／符号页面错误显示 QWERTY 下滑标签。
- 标签缓存加入当前可见按键语义，切换字母、数字、符号页面时不会复用旧标签。

## APK 核实结果

- 微信输入法版本名：3.5.2。
- APK SHA-256：`d8e8f7c90b8c85506a3b687b34df6b5df155b27446b600e8caebafa3fd497ba1`。
- 当前上传包的点击监听器：`com.tencent.wetype.plugin.hld.utils.p1`。
- 回调字段：`p1.c`，回调类：`com.tencent.wetype.plugin.hld.toolbar.A$b`。
- 工具栏状态字段仍为 `f`、`g`、`h`。

## 真机验收

1. 覆盖安装测试 APK，强制停止微信输入法后重新打开。
2. 在 26 键和九宫格分别测试“剪贴板”和“快捷发送／常用语”。
3. 切换到两级数字／符号页面，确认不再显示“剪贴、快捷、选前、选后、段首”等标签。
4. 切回字母键盘，确认标签恢复且下滑动作正常。
5. 检查正常点击、长按、滑行输入、横屏、悬浮键盘不受影响。
6. 如原生面板仍失败，导出包含 `WeTypeSwipe` 的 LSPosed 日志。

## 自动化限制

原生工具栏入口和键盘层切换依赖微信输入法运行时 View、混淆回调与 LSPosed Hook，CI 只能验证编译、单元测试、Lint 和签名，最终功能需要真机验证。
""", encoding="utf-8")

print("Applied WeType 3.5.2 panel and symbol-label regression patch")
