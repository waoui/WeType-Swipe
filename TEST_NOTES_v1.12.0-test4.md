# v1.12.0-test4 · 修复键盘上/下滑打开内置设置

## 根因和修复策略

test3 的模块动作 24 先通过 InputMethodService 尝试创建 TYPE_INPUT_METHOD_DIALOG，
在部分系统上新窗口的 token 被拒绝/窗口不可用，异常路径直接启动了
`com.rww.wetypeswipe.MainActivity` **独立模块设置**，因此用户看到错误入口。

test4 不再跳到独立模块。改为：

1. 键盘手势动作优先使用微信输入法 `com.tencent.wetype` **自身 launcher Activity**，
   在 Intent 中传递一次性的内部设置请求标记；
2. LSPosed 在目标应用的 Activity.onResume / onNewIntent / onWindowFocusChanged
   捕获请求、清除一次性标记，等到目标应用窗口已稳定后，启动原有
   `EmbeddedSettingsUi.show(activity, ...)`，即与“关于页连续点 5 次”一致的
   **内置模块设置界面**（不是独立模块 Activity）；
3. 解决启动页/重定向产生的 Activity 暂时不可用问题：
   请求在目标进程最多保持 15 秒，只有前台且有焦点、未结束的真实 Activity
   才会弹出内置 UI；
4. 如果微信输入法没有可启动的 Activity 或 Android 禁止启动 Activity，
   才尝试在原键盘窗口显示 `TYPE_INPUT_METHOD_DIALOG`。原实现误把输入法
   **键盘窗口 token** 放在前面，现在优先使用 **IME 服务 token**；
5. 两个方案均失败时只记录错误并 Toast 提示操作和日志位置，
   **绝不静默打开独立模块**。

## 保持不变

- 配置数据结构、动作 ID 0–24、L 键默认下滑设置入口、截图推荐预设
- 上滑、下滑手势识别、两个方向的文字标签排布、九宫格
- 配置导入导出（TXT/剪贴板）、独立/内置双向保存同步
- 密码框限制、原关于页五击入口

## 自动测试

```bash
./gradlew --no-daemon --stacktrace clean testDebugUnitTest lintRelease assembleRelease
```

## 必须真机验收

1. 从 v1.12.0-test3 **覆盖安装** v1.12.0-test4，无需重设 L 下滑，也无需重新登录；
2. 打开任意文本输入框，微信输入法 L 下滑 → **微信输入法自身页面**打开，
   并直接显示“微信输入法 · 内置模块设置 / 滑动快捷键”；不得打开独立模块。
3. 点击内置页面 26 键（如 Z、L）→ 方向菜单 → 动作选择 → 返回 → 保存；
   验证菜单/嵌套弹窗正常、不出现 BadTokenException、配置同步成功。
4. 重新进入键盘、验证上下滑和键帽文字仍正常；改绑其他键为动作 24 后同样可进入。
5. 检查已有上滑、预设和 TXT 配置未被重置；关于页五击仍能打开内置页面。
6. 如果遇到错误，请导出 LSPosed 日志中 `WeTypeSwipe` 附近信息，
   特别关注“keyboard swipe launched WeType Activity”、“request received”、
   “opened inside WeType Activity”和“embedded ... failed”。

## 回滚

版本：v1.12.0-test4，versionCode 65。该版为测试候选分支，
**不覆盖 v1.11.9 正式 Release，不合并 main**。
需要降回 test3 时先使用已导出的备份记录原配置，
避免因 Android 反降版本限制而采用卸载导致配置丢失。
