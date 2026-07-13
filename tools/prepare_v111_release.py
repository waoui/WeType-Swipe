from pathlib import Path
import re
import runpy

runpy.run_path("tools/patch_v111_test17_robust.py", run_name="__main__")

hook = Path("app/src/main/java/com/rww/wetypeswipe/MainHook.java")
text = hook.read_text(encoding="utf-8")
text = text.replace("v1.11.0-test17 entered target package", "v1.11.0 entered target package")
hook.write_text(text, encoding="utf-8")

activity = Path("app/src/main/java/com/rww/wetypeswipe/MainActivity.java")
text = activity.read_text(encoding="utf-8")
text = text.replace("v1.11.0-test17 · 显示选项开关", "v1.11.0 · 按键功能文字与显示选项")
activity.write_text(text, encoding="utf-8")

build = Path("app/build.gradle.kts")
text = build.read_text(encoding="utf-8")
text = re.sub(r'versionCode\s*=\s*\d+', 'versionCode = 38', text, count=1)
text = re.sub(r'versionName\s*=\s*"[^"]+"', 'versionName = "1.11.0"', text, count=1)
build.write_text(text, encoding="utf-8")

readme = Path("README.md")
text = readme.read_text(encoding="utf-8")
text = text.replace("当前稳定版本：**v1.10.0**", "当前稳定版本：**v1.11.0**")
text = text.replace("- 支持竖屏、横屏和横屏悬浮键盘\n", "- 支持竖屏、横屏、横屏悬浮键盘与分离键盘\n- 可在键帽底部显示当前下滑功能文字\n")
text = text.replace("- 可关闭模块主动震动\n", "- 可关闭模块主动震动\n- 可独立开关按键功能文字与下滑触发提示\n")
start = text.index("## v1.10.0 更新内容")
end = text.index("## 兼容性", start)
section = """## v1.11.0 更新内容

- 新增按键底部功能文字，直接显示“剪切、复制、段首、选前、选后”等绑定动作。
- 新增“显示按键底部功能文字”开关。
- 新增“显示下滑触发提示”开关，可独立控制下滑预览与执行成功提示。
- 使用微信输入法原生单键绘制链和实时键帽 `drawRect`，文字随普通、分离、悬浮和横竖屏布局同步变化。
- 深色与浅色模式分别使用高对比文字和阴影。
- 九宫格与 26 键均使用原生键帽坐标。
- 优化原生绘制热路径：缓存按键模型对应文字，未绑定按键快速返回，移除周期扫描和布局轮询。
- 将“选至段首／选至段尾”的键帽短标签调整为“选前／选后”。

完整变更请查看 [v1.11.0 Release](https://github.com/waoui/WeType-Swipe/releases/tag/v1.11.0)。

"""
readme.write_text(text[:start] + section + text[end:], encoding="utf-8")

Path("RELEASE_NOTES_v1.11.0.md").write_text("""# 微信输入法下滑快捷键 v1.11.0

## 新增功能

- 在 26 键和九宫格键帽底部常驻显示已绑定的下滑功能。
- 新增“显示按键底部功能文字”开关。
- 新增“显示下滑触发提示”开关，可独立控制下滑预览和执行成功提示。
- “选至段首”和“选至段尾”的键帽短标签调整为“选前”和“选后”。

## 显示与布局

- 直接接入微信输入法原生单键绘制链。
- 使用当前键帽的实时 `drawRect` 定位，自动跟随普通键盘、分离键盘、悬浮键盘、横竖屏和键盘缩放。
- 26 键与九宫格均使用原生键帽坐标。
- 深色模式使用浅色高对比文字，浅色模式使用深色文字。
- 根据键帽实际高度和字体 FontMetrics 自适应字号与基线。

## 性能优化

- 移除周期性布局检查、触摸扫描和行列拟合的正常路径。
- 缓存“按键模型 → 最终显示文字”，避免持续解析按键 ID 和重复查询配置。
- 未绑定按键快速返回；关闭功能文字后在读取键帽坐标前直接返回。
- 仅已绑定且开启显示的按键增加一次文字绘制。

## 兼容性

- Android 8.0 及以上。
- LSPosed 环境。
- 当前实测微信输入法 3.5.0、Android 16。

安装后请在 LSPosed 中启用模块并勾选“微信输入法”作用域，然后重启微信输入法进程或设备。
""", encoding="utf-8")

print("v1.11.0 release source prepared")
