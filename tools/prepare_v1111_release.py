from pathlib import Path
import re
import runpy

runpy.run_path("tools/patch_v1111_test1_compile_fix.py", run_name="__main__")

hook = Path("app/src/main/java/com/rww/wetypeswipe/MainHook.java")
text = hook.read_text(encoding="utf-8")
text = text.replace("v1.11.1-test1 entered target package", "v1.11.1 entered target package")
hook.write_text(text, encoding="utf-8")

activity = Path("app/src/main/java/com/rww/wetypeswipe/MainActivity.java")
text = activity.read_text(encoding="utf-8")
text = text.replace(
    "v1.11.1-test1 · 全复制、全剪切与自定义标签",
    "v1.11.1 · 全复制、全剪切与自定义标签",
)
activity.write_text(text, encoding="utf-8")

build = Path("app/build.gradle.kts")
text = build.read_text(encoding="utf-8")
text = re.sub(r"versionCode\s*=\s*\d+", "versionCode = 39", text, count=1)
text = re.sub(r'versionName\s*=\s*"[^"]+"', 'versionName = "1.11.1"', text, count=1)
build.write_text(text, encoding="utf-8")

readme = Path("README.md")
text = readme.read_text(encoding="utf-8")
text = text.replace("当前稳定版本：**v1.11.0**", "当前稳定版本：**v1.11.1**")
section = """## v1.11.1 更新内容

- 新增“复制全部”：自动全选并复制全部文本，完成后恢复原光标或选区。
- 新增“剪切全部”：自动全选并剪切全部文本，失败时恢复原选区。
- 26 键和九宫格支持长按按键设置显示标签。
- 标签支持自动、自定义和隐藏三种模式，自定义内容最多 4 个字符。
- 保留全局“显示按键底部功能文字”总开关。
- 配置保存后立即刷新原生单键文字缓存。

"""
if "## v1.11.1 更新内容" not in text and "## 兼容性" in text:
    text = text.replace("## 兼容性", section + "## 兼容性", 1)
readme.write_text(text, encoding="utf-8")

Path("release-notes-v1.11.1.md").write_text(
    """# 微信输入法下滑快捷键 v1.11.1

## 新增功能

- **复制全部**：全选当前输入框内容并复制，随后恢复原光标或选区。
- **剪切全部**：全选当前输入框内容并剪切；执行失败时恢复原选区。
- **自定义按键标签**：26 键和九宫格均可长按按键设置标签。
- 标签支持自动、自定义和隐藏三种模式，自定义内容最多 4 个字符。

## 使用说明

- 点击按键设置下滑动作。
- 长按按键设置该按键的显示标签。
- 全局“显示按键底部功能文字”开关仍可统一控制所有标签。
- 安装后请在 LSPosed 中启用模块，并重启微信输入法进程。

## 兼容性

- Android 8.0 及以上
- LSPosed
- 安卓版微信输入法
- 当前主要验证版本：微信输入法 3.5.0
""",
    encoding="utf-8",
)

for path in (
    hook,
    activity,
    build,
):
    if "1.11.1-test1" in path.read_text(encoding="utf-8"):
        raise RuntimeError(f"test version marker remains in {path}")

print("Prepared v1.11.1 formal source")
