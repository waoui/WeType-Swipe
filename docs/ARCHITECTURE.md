# 模块架构

## 分层

- `MainHook`：只负责 Xposed Hook 编排、手势状态、标签绘制和动作调度。
- `ActionRegistry`：动作 ID、名称、短标签、菜单顺序、26 键存储字段和动作类别的唯一来源。
- `ConfigCodec`：模块配置在 SharedPreferences / Intent / 目标缓存之间的统一序列化。
- `ConfigBridge`：微信输入法进程内的配置广播、缓存和热更新。
- `KeyboardCompat`：微信输入法自绘键盘基类与手写上下文识别。
- `KeyResolver`：将微信输入法内部按键模型解析为稳定的 QWERTY / T9 键值。
- `Reflector`：混淆成员调用的缓存反射工具。
- `ToolbarCarrierLayout`：微信输入法原生剪贴板 / 快捷发送工具栏载体兼容。

## 维护规则

1. 新动作 ID 继续只允许向后追加；动作元数据先登记到 `ActionRegistry`，不要在 UI、Config 和 Hook 中分别复制动作数组/名称。
2. 新配置字段优先进入 `ConfigCodec`，保证模块设置、广播快照和目标缓存一次同步。
3. 微信输入法版本兼容优先落到 `KeyboardCompat`、`KeyResolver` 或专用 Bridge，不再把版本判断堆回 `MainHook`。
4. 重构不得改变动作 ID、默认键位、密码框隔离、手势阈值和已验证的微信输入法兼容语义。
5. 每次新增动作或配置字段都必须补注册完整性/配置往返测试。
