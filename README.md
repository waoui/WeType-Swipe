# 微信输入法下滑快捷键（WeType Swipe）

适用于安卓版微信输入法的 LSPosed 模块，可为 26 键字母和九宫格 `2–9` 实体键配置下滑快捷操作。

> 当前稳定版本：v1.9.4

## 下载

- [前往 GitHub Releases](https://github.com/waoui/WeType-Swipe/releases/latest)
- [直接下载 v1.9.4 APK](https://github.com/waoui/WeType-Swipe/releases/download/v1.9.4/WeType_Swipe_LSPosed_v1.9.4.apk)

请仅从本仓库 Releases 下载正式版本，并核对发布页中的 SHA-256。

## 功能

- 全选、剪切、复制、粘贴
- 段首、段尾
- 选至段首、选至段尾
- 指定按键禁用下滑
- 26 键与九宫格独立映射和触发距离
- QWERTY 与九宫格键盘式设置界面
- 支持关闭主动震动和隐藏桌面图标
- 不联网，不收集或保存输入内容

## v1.9.4

- 新增段落定位和段落范围选择操作
- 修复段落操作在普通输入框中不生效的问题
- 修复 Android 15/16 顶栏与状态栏重叠
- 26 键改为标准 QWERTY 键盘布局
- 九宫格设置仅展示 `1–9`，其中 `2–9` 可配置
- 保持 v1.8.6 已验证的九宫格配置同步与手势逻辑

## 使用条件

- Android 8.0 及以上
- LSPosed / Modern Xposed API 101+
- 当前实测：微信输入法 3.5.0、Android 16

## 构建

需要 JDK 17、Android SDK 35。Modern Xposed API 通过 `compileOnly` 引入，不会打包进 APK。

## 许可

Apache License 2.0。
