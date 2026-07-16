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
old_carrier = '''            if (view.hasOnClickListeners() || view.isClickable()) {
                View.OnClickListener listener = readOnClickListener(view);
                if (listener != null && "com.tencent.wetype.plugin.hld.utils.h3".equals(listener.getClass().getName())) {
                    Object callback = readNamedField(listener, "c");
                    if (callback != null
                            && "com.tencent.wetype.plugin.hld.toolbar.a0$b".equals(callback.getClass().getName())
                            && readNamedField(callback, "this$0") != null) {
                        return new Object[]{view, listener, callback};
                    }
                }
            }
'''
new_carrier = '''            if (view.hasOnClickListeners() || view.isClickable()) {
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
'''
replace_once(main_hook, old_carrier, new_carrier)
replace_once(main_hook,
             'logInfo("v1.11.1 entered target package");',
             'logInfo("v1.11.2-test1 entered target package; WeType 3.5.2 adapter enabled");')

main_activity = ROOT / "app/src/main/java/com/rww/wetypeswipe/MainActivity.java"
replace_once(main_activity,
             'v1.11.1 · 全复制、全剪切与自定义标签',
             'v1.11.2-test1 · 微信输入法 3.5.2 兼容测试')

gradle_properties = ROOT / "gradle.properties"
properties = gradle_properties.read_text(encoding="utf-8")
properties, code_count = re.subn(r"(?m)^VERSION_CODE=.*$", "VERSION_CODE=40", properties, count=1)
properties, name_count = re.subn(r"(?m)^VERSION_NAME=.*$", "VERSION_NAME=1.11.2-test1", properties, count=1)
if code_count != 1 or name_count != 1:
    raise SystemExit("Could not update VERSION_CODE/VERSION_NAME")
gradle_properties.write_text(properties, encoding="utf-8")

notes = ROOT / "TEST_NOTES_v1.11.2-test1.md"
notes.write_text("""# 微信输入法下滑快捷键 v1.11.2-test1

## 本次测试目标

- 适配微信输入法 3.5.2（versionCode 54204）。
- 修复下滑打开原生剪贴板失效。
- 修复下滑打开快捷发送／常用语失效。
- 保留微信输入法 3.5.0 的旧入口兼容。

## 已核实的 3.5.2 内部结构

- 点击监听器：`com.tencent.wetype.plugin.hld.utils.o1`
- 工具栏回调：`com.tencent.wetype.plugin.hld.toolbar.A$b`
- 外层工具栏：`com.tencent.wetype.plugin.hld.toolbar.A`
- 功能、来源、分组字段仍为 `f`、`g`、`h`

## 测试方法

1. 直接覆盖安装测试 APK。
2. 在 LSPosed 中确认模块作用域仍为“微信输入法”。
3. 强制停止微信输入法后重新启用。
4. 分别测试 26 键和九宫格绑定的“剪贴板”“快捷发送”。
5. 如失败，导出包含 `WeTypeSwipe` 的 LSPosed 日志。
""", encoding="utf-8")

print("Applied WeType 3.5.2 compatibility patch")
