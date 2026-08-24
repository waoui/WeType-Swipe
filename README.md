# 微信输入法下滑快捷键

为安卓版微信输入法增加自定义按键下滑操作的 LSPosed 模块。

支持 26 键与九宫格，可将常用编辑操作、原生剪贴板、快捷发送以及自定义固定文本绑定到指定按键。正常点击仍保持原有输入，下滑时执行快捷功能。

[![Latest Release](https://img.shields.io/github/v/release/waoui/WeType-Swipe?label=最新版)](https://github.com/waoui/WeType-Swipe/releases/latest)
[![Android](https://img.shields.io/badge/Android-8.0%2B-3DDC84)](#兼容性)
[![License](https://img.shields.io/github/license/waoui/WeType-Swipe)](LICENSE)

## 下载

请从本仓库的 [Releases 页面](https://github.com/waoui/WeType-Swipe/releases/latest) 下载正式版 APK。

当前稳定版本：**v1.11.6**

> 建议同时下载发布页中的 SHA256 校验文件，确认 APK 完整且未被修改。

## 主要功能

### 快捷操作

- 全选、剪切、复制、粘贴
- 复制全部、剪切全部
- 移动到段首、段尾
- 选择当前位置到段首、段尾
- 移动到整篇文本的文首、文尾
- 选择当前位置到整篇文本的文首、文尾
- 打开微信输入法原生剪贴板
- 打开微信输入法原生快捷发送／常用语
- 撤销、重做
- 输入指定内容：每个按键可保存独立文本，支持中文、英文、数字、符号、Emoji 和换行
- 禁用指定按键的下滑动作

### 键盘与手势

- 支持 26 键字母区
- 支持九宫格数字键 2–9
- 26 键与九宫格可独立配置
- “输入指定内容”可同时绑定多个按键，每个按键内容互不影响
- 26 键与九宫格可分别调整触发距离
- 支持竖屏、横屏、横屏悬浮键盘与分离键盘
- 可在键帽底部显示当前下滑功能文字
- 可长按按键设置自动、自定义或隐藏标签
- 原生剪贴板与快捷发送无需显示在输入法工具栏

### 设置与隐私

- QWERTY 与九宫格键盘式设置界面
- 独立模块 APK 与内置模块模式使用一致的主要设置界面
- 内置模块模式可在微信输入法“关于”页面连续点击图标 5 次打开设置
- 可关闭模块主动震动
- 可独立开关按键功能文字与下滑触发提示
- 独立 APK 模式可隐藏桌面图标，并从 LSPosed 模块设置重新进入
- 模块不联网，不采集或上传实际输入内容
- “输入指定内容”由用户主动配置，内容仅保存在本机模块／目标应用配置中

## 安装与使用

### 独立 APK 模式

1. 安装最新版 APK。
2. 在 LSPosed 中启用本模块。
3. 将模块作用域勾选为“微信输入法”。
4. 强制停止并重新启动微信输入法，或重启设备。
5. 打开“微信输入法下滑快捷键”，点击键位设置对应动作。
6. 点击底部“保存并应用配置”。

### 内置模块模式

如果模块被内置后无法打开独立设置 APK：

1. 打开微信输入法的“关于”页面。
2. 在同一位置连续点击页面图标 **5 次**。
3. 在弹出的内置设置页中配置并保存。

如修改配置后没有立即生效，请重新启动微信输入法进程。

## 默认配置

| 按键 | 下滑动作 |
| --- | --- |
| Z | 全选 |
| X | 剪切 |
| C | 复制 |
| V | 粘贴 |

其他操作默认不绑定，可在模块设置中自由分配。一个按键同一时刻只执行一个下滑动作；“输入指定内容”属于可重复动作，可以配置到多个按键，并为每个按键保存不同内容。

## v1.11.6 更新内容

- 新增内置模块设置入口：微信输入法“关于”页图标连续点击 5 次打开设置。
- 内置设置页与独立模块设置页统一 26 键、九宫格、手势、显示反馈和保存交互。
- 新增“输入指定内容”动作，26 键与九宫格 2–9 均支持，每个按键保存独立文本。
- 指定内容最多 1000 个 Unicode 字符，支持中文、英文、数字、符号、Emoji 和换行。
- 输入前结束当前 composing 状态，再通过 `InputConnection.commitText()` 插入，不占用系统剪贴板。
- 新动作编号追加为 20，原有 0–19 编号、默认键位和既有配置保持兼容。

完整变更请查看 [v1.11.6 Release](https://github.com/waoui/WeType-Swipe/releases/tag/v1.11.6) 和 [更新记录](CHANGELOG.md)。

## 兼容性

- Android 8.0 及以上
- LSPosed 环境
- 安卓版微信输入法
- 当前实测：微信输入法 3.5.0、3.5.2，Android 16

微信输入法升级后，内部实现变化可能影响原生剪贴板、快捷发送或界面匹配。如遇兼容问题，请在 Issues 中附上微信输入法版本、Android 版本、LSPosed 日志和复现步骤。

## 构建

构建环境：

- JDK 17
- Android SDK 35
- Gradle 8.9

Modern Xposed API 以 `compileOnly` 方式引入，不会打包进 APK。

```bash
./gradlew clean testDebugUnitTest lintDebug assembleDebug
```

Windows 可将命令中的 `./gradlew` 改为 `gradlew.bat`。版本号统一维护在 `gradle.properties` 的 `VERSION_CODE` 和 `VERSION_NAME` 中。

### 发布正式版

1. 更新 `VERSION_CODE`、`VERSION_NAME`、`CHANGELOG.md`、`README.md` 和对应的 `RELEASE_NOTES_v版本号.md`。
2. 合并代码并等待持续集成通过。
3. 在 Actions 中手动运行“构建并发布正式版”，或由仓库所有者创建标题为 `Publish v版本号 final` 的安全发布触发 PR／Issue。
4. 工作流从 `main` 检出正式源码，执行单元测试、Lint、正式签名验证，并上传 APK、源码 ZIP 和 SHA-256 校验文件。

历史版本说明以 GitHub Release、Tag 和 `CHANGELOG.md` 为准；已发布旧版本的 `RELEASE_NOTES_v*.md` 无需长期保留在 `main`。

未配置正式签名环境变量时，构建产物不会使用项目的发布证书。正式 Release 由 GitHub Actions 使用仓库 Secrets 自动签名、校验并发布。

## 许可

本项目基于 [Apache License 2.0](LICENSE) 开源。
