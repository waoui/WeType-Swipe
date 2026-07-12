# 微信输入法下滑快捷键（WeType Swipe）

适用于安卓版微信输入法的 LSPosed 模块，可为 26 键字母和九宫格 2–9 实体键配置下滑快捷操作。

> 当前稳定版本：v1.8.6

## 功能

- 26 键支持全选、剪切、复制、粘贴和禁用下滑
- 九宫格 2–9 支持独立配置
- 正常点击仍由微信输入法处理
- 26 键与九宫格可分别设置触发距离
- 可关闭模块主动震动
- 可隐藏桌面图标
- 不联网，不收集或保存输入内容

## 下载

- [前往 GitHub Releases](https://github.com/waoui/WeType-Swipe/releases/latest)
- [直接下载 v1.8.6 APK](https://github.com/waoui/WeType-Swipe/releases/download/v1.8.6/WeType_Swipe_LSPosed_v1.8.6.apk)

请仅从本仓库 Releases 下载正式版本，并核对发布页中的 SHA-256。

## 环境

- Android 8.0 及以上
- LSPosed / Modern Xposed API 101+
- 微信输入法，当前测试版本为 3.5.0

## 使用

1. 安装 Release 页面中的 APK。
2. 在 LSPosed 中启用模块，作用域选择微信输入法。
3. 重启微信输入法进程或重启手机。
4. 打开模块设置按键映射并保存。

## 构建

需要 JDK 17、Android SDK 35。使用 Android Studio 打开项目，或执行：

```bash
./gradlew assembleRelease
```

Modern Xposed API 通过 `compileOnly` 引入，不会打包进 APK。

## 发布与签名

仓库不包含发布私钥、keystore、密码或签名配置。正式版本必须使用项目维护者保存的固定发布密钥签名。

当前固定签名证书 SHA-256：

```text
1082df3bac441e9bd020ce640d66924de6c7dfb70836b262743e15777863c93a
```

## 许可

Apache License 2.0。
