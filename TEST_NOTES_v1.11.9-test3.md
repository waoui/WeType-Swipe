# v1.11.9-test3 性能优化测试

基于 v1.11.9-test2，功能和配置语义不变。

## 优化点
- 键盘 View 首次识别后缓存 QWERTY/T9/手写模式，避免触摸和绘制热路径重复扫描父 View/类名。
- 键盘绘制 Hook 按 Class 一次性准备，避免每次触摸进入 synchronized + 反射查找。
- 原生单键 Hook 未就绪时改为 2 秒退避探测，不再每个触摸事件重复 Class/Method 查找。
- fallback 绘制直接使用 currentEditorPassword，不再每帧调用 getCurrentInputEditorInfo。
- 原生单键绘制只读取一次 Config。
- 亮暗主题改为 Configuration 回调驱动缓存；正常单键绘制只做 volatile 主题读取，保留旧 View 配置兜底。
- 隐藏设置五击检测仅在 ACTION_UP 进入。

## 回归重点
1. 26 键/九宫格下滑动作保持一致。
2. 手写、数字、符号页不出现功能标签。
3. 亮色↔暗色热切换仍即时刷新。
4. 剪贴板、常用语、指定文本、输入法切换正常。
5. 关于页 5 击设置正常。
