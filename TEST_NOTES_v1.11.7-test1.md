# v1.11.7-test1 测试说明

目标：修复微信输入法 4.0.0（上传 APK：versionCode 57201）中下滑模块整体失效。

## 已确认的静态变化

- 旧版模块识别自绘键盘公共基类：`com.tencent.wetype.plugin.hld.keyboard.selfdraw.n`。
- 微信输入法 4.0.0 中 `selfdraw.n` 已变为普通 `Runnable`，不再是键盘基类。
- 4.0.0 的 26 键/九宫格继承链共同经过 `selfdraw.o`：
  - `S2ChineseQwertyKeyboard -> b -> o -> keyboard.s -> LinearLayout`
  - `S1ChineseT9Keyboard -> c -> o -> keyboard.s -> LinearLayout`
- `selfdraw.o` 仍提供 `getActionButton()`、`getKeysLayoutInfo()`；按键模型 `selfdraw.j` 与单键绘制器 `drawmethod.c/d` 仍存在。

## test1 修复

- 同时兼容旧基类 `selfdraw.n` 与 4.0.0 基类 `selfdraw.o`。
- 增加结构特征回退：在 `selfdraw` 命名空间中寻找“本类声明 `getActionButton()` + `getKeysLayoutInfo()` 的 View 基类”，避免以后单字母混淆名再次变化导致整个模块失效。
- 不改变动作 ID、配置格式、默认键位和 v1.11.6 功能语义。

## 真机重点验收

1. 微信输入法 4.0.0 26 键：Z/X/C/V 默认下滑恢复。
2. 自定义动作和“输入指定内容”恢复。
3. 九宫格 2–9 自定义下滑恢复。
4. 数字/符号页、手写页不误触发。
5. 按键底部功能文字、下滑提示正常。
6. 原生剪贴板、快捷发送/常用语分别测试一次。
7. 关于页图标连续 5 击仍可打开内置模块设置。
8. 旧版微信输入法 3.5.2 如方便可做一次回归，确认旧 `selfdraw.n` 兼容未受影响。
