# 微信输入法下滑快捷键

为安卓版微信输入法增加自定义按键下滑操作的 LSPosed 模块。

支持 26 键与九宫格，可将常用编辑操作、原生剪贴板和快捷发送绑定到指定按键。正常点击仍保持原有输入，下滑时执行快捷功能。

[![Latest Release](https://img.shields.io/github/v/release/waoui/WeType-Swipe?label=最新版)](https://github.com/waoui/WeType-Swipe/releases/latest)
[![Android](https://img.shields.io/badge/Android-8.0%2B-3DDC84)](#兼容性)
[![License](https://img.shields.io/github/license/waoui/WeType-Swipe)](LICENSE)

## 下载

请从本仓库的 [Releases 页面](https://github.com/waoui/WeType-Swipe/releases/latest) 下载正式版 APK。

当前稳定版本：**v1.11.4**

> 建议同时下载发布页中的 SHA256 校验文件，确认 APK 完整且未被修改。

## 主要功能

### 快捷操作

- 全选、剪切、复制、粘贴
- 复制全部、剪切全部
- 移动到段首、段尾
- 选择当前位置到段首、段尾
- 打开微信输入法原生剪贴板
- 打开微信输入法原生快捷发送／常用语
- 撤销、重做
- 禁用指定按键的下滑动作

### 键盘与手势

- 支持 26 键字母区
- 支持九宫格数字键 2–9
- 26 键与九宫格可独立配置
- 26 键与九宫格可分别调整触发距离
- 支持竖屏、横屏、横屏悬浮键盘与分离键盘
- 可在键帽底部显示当前下滑功能文字
- 可长按按键设置自动、自定义或隐藏标签
- 原生剪贴板与快捷发送无需显示在输入法工具栏

### 设置与隐私

- QWERTY 与九宫格键盘式设置界面
- 可关闭模块主动震动
- 可独立开关按键功能文字与下滑触发提示
- 可隐藏桌面图标，并从 LSPosed 模块设置重新进入
- 不联网，不收集、上传或保存输入内容

## 安装与使用

1. 安装最新版 APK。
2. 在 LSPosed 中启用本模块。
3. 将模块作用域勾选为“微信输入法”。
4. 强制停止并重新启动微信输入法，或重启设备。
5. 打开“微信输入法下滑快捷键”，点击键位设置对应动作。
6. 点击底部“保存并应用配置”。

如修改配置后没有立即生效，请重新启动微信输入法进程。

## 默认配置

| 按键 | 下滑动作 |
| --- | --- |
| Z | 全选 |
| X | 剪切 |
| C | 复制 |
| V | 粘贴 |

其他操作默认不绑定，可在模块设置中自由分配。同一个按键不能同时绑定多个动作。

## v1.11.4 更新内容

- 新增“撤销”和“重做”下滑动作，26 键与九宫格均可绑定。
- 使用 Android 标准编辑器撤销／重做指令，不保存输入内容，也不维护私有撤销栈。
- 触发前结束当前输入法组词状态，再由目标 App 的输入框执行撤销或重做。
- 中文输入可能按“中文 → 拼音 → 空白”的顺序撤销，这是目标编辑器对组词和上屏记录为两个步骤的正常表现。
- 保持数字、符号、手写键盘和密码输入框的隔离逻辑不变。
- 保持 v1.11.3 的原生剪贴板、快捷发送和标签兼容修复不变。

完整变更请查看 [v1.11.4 Release](https://github.com/waoui/WeType-Swipe/releases/tag/v1.11.4) 和 [更新记录](CHANGELOG.md)。

## 兼容性

- Android 8.0 及以上
- LSPosed 环境
- 安卓版微信输入法
- 当前实测：微信输入法 3.5.0、3.5.2，Android 16

微信输入法升级后，内部实现变化可能影响原生剪贴板或快捷发送功能。如遇兼容问题，请在 Issues 中附上微信输入法版本、Android 版本、LSPosed 日志和复现步骤。

## 构建

构建环境：

- JDK 17
- Android SDK 35
- Gradle 8.9

Modern Xposed API 以 `compileOnly` 方式引入，不会打包进 APK。

```bash
./gradlew clean testDebugUnitTest lintDebug assembleDebug
```

Windows 可将命令中的 `./gradlew` 改为 `gradlew.bat`。版本号统一维护在
`gradle.properties` 的 `VERSION_CODE` 和 `VERSION_NAME` 中。

### 发布正式版

1. 更新 `VERSION_CODE`、`VERSION_NAME` 和对应的 `RELEASE_NOTES_v版本号.md`。
2. 合并代码并等待持续集成通过。
3. 在 Actions 中手动运行“构建并发布正式版”，或由仓库所有者创建标题为
   `Publish v版本号 final` 的 Issue。
4. 工作流会执行单元测试、Lint、正式签名验证，并上传 APK、源码 ZIP 和 SHA-256 校验文件。

未配置正式签名环境变量时，构建产物不会使用项目的发布证书。正式 Release 由 GitHub Actions 使用仓库 Secrets 自动签名、校验并发布。

## 许可

本项目基于 [Apache License 2.0](LICENSE) 开源。
