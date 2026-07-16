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
    'logInfo("v1.11.1 entered target package");',
    'logInfo("v1.11.2 entered target package; WeType 3.5.0/3.5.2 adapters enabled");',
)
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

main_activity = ROOT / "app/src/main/java/com/rww/wetypeswipe/MainActivity.java"
replace_once(
    main_activity,
    'v1.11.1 · 全复制、全剪切与自定义标签',
    'v1.11.2 · 兼容微信输入法 3.5.2',
)

gradle_properties = ROOT / "gradle.properties"
properties = gradle_properties.read_text(encoding="utf-8")
properties, code_count = re.subn(r"(?m)^VERSION_CODE=.*$", "VERSION_CODE=40", properties, count=1)
properties, name_count = re.subn(r"(?m)^VERSION_NAME=.*$", "VERSION_NAME=1.11.2", properties, count=1)
if code_count != 1 or name_count != 1:
    raise SystemExit("Could not update VERSION_CODE/VERSION_NAME")
gradle_properties.write_text(properties, encoding="utf-8")

changelog = ROOT / "CHANGELOG.md"
text = changelog.read_text(encoding="utf-8")
prefix = "# 更新记录\n\n"
if not text.startswith(prefix):
    raise SystemExit("Unexpected CHANGELOG header")
entry = '''## v1.11.2

- 修复微信输入法 3.5.2 下滑打开原生剪贴板失效
- 修复微信输入法 3.5.2 下滑打开快捷发送／常用语失效
- 同时兼容微信输入法 3.5.0 与 3.5.2 的原生工具栏入口
- 增加原生工具栏载体匹配日志，便于后续版本兼容排查

'''
changelog.write_text(prefix + entry + text[len(prefix):], encoding="utf-8")

readme = ROOT / "README.md"
text = readme.read_text(encoding="utf-8")
text = text.replace("当前稳定版本：**v1.11.1**", "当前稳定版本：**v1.11.2**", 1)
start = text.index("## v1.11.1 更新内容")
end = text.index("## 兼容性", start)
release_section = '''## v1.11.2 更新内容

- 修复微信输入法 3.5.2 下滑打开原生剪贴板失效。
- 修复微信输入法 3.5.2 下滑打开快捷发送／常用语失效。
- 保留微信输入法 3.5.0 原生工具栏入口兼容。
- 增加原生工具栏载体匹配日志，便于后续版本升级时定位兼容问题。

完整变更请查看 [v1.11.2 Release](https://github.com/waoui/WeType-Swipe/releases/tag/v1.11.2) 和 [更新记录](CHANGELOG.md)。

'''
text = text[:start] + release_section + text[end:]
text = text.replace(
    "- 当前实测：微信输入法 3.5.0、Android 16",
    "- 当前实测：微信输入法 3.5.0、3.5.2，Android 16",
    1,
)
readme.write_text(text, encoding="utf-8")

notes = ROOT / "RELEASE_NOTES_v1.11.2.md"
if notes.exists():
    raise SystemExit(f"{notes} already exists")
notes.write_text('''# 微信输入法下滑快捷键 v1.11.2

## 修复内容

- 修复微信输入法 3.5.2 中，下滑打开原生剪贴板无响应的问题。
- 修复微信输入法 3.5.2 中，下滑打开快捷发送／常用语无响应的问题。
- 保留微信输入法 3.5.0 的原生工具栏入口兼容。
- 增加原生工具栏载体匹配日志，便于后续微信输入法版本升级时定位兼容问题。

## 兼容性

- Android 8.0 及以上
- LSPosed
- 安卓版微信输入法 3.5.0、3.5.2
- 已在 Android 16 环境验证

## 安装说明

1. 可直接覆盖安装 v1.11.1。
2. 在 LSPosed 中确认模块已启用，作用域勾选“微信输入法”。
3. 强制停止并重新启动微信输入法，或重启设备。
4. 原有按键配置会保留。
''', encoding="utf-8")

# Promotion files are intentionally one-shot and must not remain in main.
(ROOT / ".github/workflows/promote-v1.11.2.yml").unlink()
Path(__file__).unlink()
print("Prepared v1.11.2 release sources")
