# WeType-Swipe v1.11.7-test2 真机测试

目标：在微信输入法 4.0.0 上恢复原生剪贴板与快捷发送／常用语入口，同时保留 test1 已恢复的基础下滑。

## 本版修复

- 继承 test1：兼容 4.0.0 自绘键盘公共基类 `selfdraw.o`，同时保留旧版 `selfdraw.n` 与结构特征回退。
- 兼容 4.0.0 工具栏 ViewHolder 字段从旧 `f(int)/g(enum)/h(int)` 变为 `g(int)/h(enum)/i(int)`。
- 载体解析优先支持已知旧/新字段布局，并保留“function int -> Permanent source enum -> group int”的结构回退。
- 4.0.0 点击回调新增 Main.immediate 协程包装；test2 在识别到新字段布局时直接调用具体 ViewHolder 的 `g(View)` 点击处理方法，确保临时目标 function/source/group 在处理时仍然有效。
- 剪贴板 function bit 继续为 `4`，快捷发送／常用语 function bit 继续为 `8`；已通过 4.0.0 DEX 的 toolbar switch 表静态核对。

## 请重点验收

1. 26 键绑定“剪贴板”，下滑后是否直接打开微信输入法原生剪贴板。
2. 26 键绑定“快捷发送／常用语”，下滑后是否打开对应原生面板。
3. 九宫格分别绑定这两个动作，确认同样生效。
4. 连续从剪贴板 -> 返回键盘 -> 常用语 -> 返回键盘，多次切换，确认不会打开错误面板。
5. 再测一次普通复制/粘贴/指定内容，确认 test1 的基础下滑没有回归。
6. 数字／符号页和手写页仍不应误触发模块动作。

## 版本

- versionName: `1.11.7-test2`
- versionCode: `52`
- 目标微信输入法：`4.0.0 / 57201`
- 真机通过前不合并、不发布正式版、不同步 LSPosed 官方仓库。
