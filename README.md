# 微信输入法下滑快捷键（WeType Swipe）

为安卓版微信输入法增加可自定义的按键下滑操作，支持 **26 键和九宫格键盘**，基于 LSPosed / Modern Xposed API 102。

> 当前源码版本：v1.8.0 公测版  
> 仓库源码已修正为与 v1.8.0 APK 对应的 `versionCode 9` 版本。

## 功能

- 26 键任意 A–Z 字母可绑定下滑动作
- 九宫格 `2–9` 实体键可独立绑定下滑动作
- 支持全选、剪切、复制、粘贴和禁用下滑
- 26 键与九宫格配置相互独立
- 正常点击按键仍由微信输入法处理
- 未绑定按键完全放行
- 26 键和九宫格可分别设置触发距离
- 可关闭模块主动触发的震动
- 支持隐藏桌面图标
- 静态作用域仅为微信输入法 `com.tencent.wetype`
- 不修改微信输入法 APK

## 默认映射

### 26 键

| 按键 | 下滑动作 |
|---|---|
| Z | 全选 |
| X | 剪切 |
| C | 复制 |
| V | 粘贴 |

### 九宫格

九宫格 `2 / ABC` 至 `9 / WXYZ` 默认均为“未绑定”，需要在模块设置中自行配置。

## 使用方法

1. 安装 APK。
2. 在 LSPosed 中启用本模块。
3. 确认作用域为“微信输入法”。
4. 重启微信输入法进程或重启手机。
5. 打开模块并设置 26 键或九宫格映射。

## 下载

发布版本统一在 [Releases 页面](https://github.com/waoui/WeType-Swipe/releases) 下载。

v1.7.0 APK：[直接下载](https://github.com/waoui/WeType-Swipe/releases/download/v1.7.0/WeType_Swipe_LSPosed_v1.7.0.apk)

## 源码状态

当前 `main` 分支对应 v1.8.0，主要源码包括：

- `Config.java`
- `ConfigProvider.java`
- `DiagnosticReceiver.java`
- `MainActivity.java`
- `MainHook.java`

构建配置：

```text
versionCode 9
versionName 1.8.0
minSdk 26
targetSdk 35
Modern Xposed API 102
```

仓库不会包含发布私钥、keystore 或密码。

## 已测试环境

- 微信输入法：3.5.0
- Android：16
- 架构：arm64
- 框架：LSPosed

其他系统版本和微信输入法版本尚未全部验证。

## 注意事项

- 当前适配微信输入法 26 键拼音、英文键盘和九宫格 `2–9`。
- 九宫格 `0、1、删除、空格、回车` 暂不参与下滑绑定。
- 手写和符号面板未专项适配。
- 关闭模块震动后，如果仍有按键震动，可能是微信输入法自身的按键反馈。
- 模块不联网，不收集、上传或保存输入内容。

## 问题反馈

反馈时请提供：

```text
手机型号：
系统版本：
微信输入法版本：
LSPosed 版本：
使用布局：26 键 / 九宫格
失效的绑定：
是否所有应用都失效：
运行状态截图：
LSPosed 日志：
```

## v1.8.0

- 新增九宫格 `2–9` 独立映射
- 自动区分 26 键和九宫格
- 新增九宫格独立触发距离
- 九宫格使用更严格的纵向手势判断
- 保留 v1.7.0 稳定触摸 Hook 链路
- 沿用固定签名，可覆盖安装 v1.7.0

完整记录见 [CHANGELOG.md](CHANGELOG.md)。

## 签名证书

固定签名证书 SHA-256：

```text
5605d7277327f226a9a3ae56e65c65532ed54d220c57bdd888eab112dd1d344f
```

## 开源许可

本项目采用 [Apache License 2.0](LICENSE) 开源。
