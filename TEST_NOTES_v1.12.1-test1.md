# v1.12.1-test1：修复输入法内置设置与独立模块 App 不同步

## 已确认的问题
v1.12.0 中，微信输入法内置设置由目标进程持有，独立模块 App 另有一份 SharedPreferences：
- 内置保存只尝试单向发一次显式 CONFIG_CHANGED 广播到模块 Manifest Receiver。
- ConfigSyncReceiver 未检查 editor.commit() 返回值，异常被吞掉，没有失败日志。
- WeTypeSwipeApplication 只在 Activity 返回前台时按 _external_sync_pending 重建；若模块 App **一直在前台**时收到更新，不会立即刷新。
- onActivityCreated 会无条件删除 _external_sync_pending，可能过早消耗提醒。
- 模块 App 不会向输入法主动请求最新已生效配置，因此漏掉一次广播后状态可能长期分叉。

## test1 修复
1. ConfigBridge 注册 ACTION_CONFIG_REQUEST；独立模块打开或返回前台时主动询问当前运行的微信输入法配置。
2. 输入法若有已加载的持久化配置，向模块已有的 ConfigSyncReceiver 回传**完整快照**。无需重装、无需手动在内置设置里重新保存。
3. 模块 Receiver 校验修订号，拒绝比本地更旧的快照；明确记录写入结果和异常，避免静默丢失。
4. 模块 App 新增 SharedPreferences 实时变更监听：有新快照时刷新 26 键、九宫格、上/下滑、标签及手势选项。
5. 若独立 App 当前有尚未保存的编辑，弹窗要求用户决定是否刷新，不静默覆盖输入内容。保存时阻止未处理的同步冲突。
6. 设置页的“配置备份与恢复”新增 **从微信输入法读取最新配置** 按钮，供漏广播时手动补拉。
7. 移除可能提前清除同步标记的旧 ActivityLifecycleCallbacks 逻辑，不改手势识别、L 键进入内置设置、动作列表、绘制及旧配置字段。
8. 新增 ConfigFingerprintTest 验证配置深拷贝、一切方向修改可检测、版本号变化不会被误当成用户编辑。

## 实际行为与限制
- 若微信输入法进程没有运行，其动态 BroadcastReceiver 不能立即响应请求。先在任意文本输入框打开微信输入法、返回模块 App，或点击手动同步，再查看键位。
- 输入法修订号低于独立 App 时，自动同步保护性拒绝并提示版本冲突，防止刚从独立 App 保存的新设置被旧数据覆盖。用户可在“配置备份与恢复”中手动确认“以微信输入法配置为准”；该确认仅 15 秒有效，并将修订号递增后同步回输入法，避免后续再次分叉。
- **自动化测试无法直接证明不同 Android ROM 的跨应用广播一定送达**，需用户真机验收。新日志标记：WeTypeSwipeSync，输入法日志：embedded settings saved / responded to module config refresh request。

## 验收
1. 在微信输入法 **内置模块设置** 将 L 下滑绑定“内置模块设置”并保存，切到独立模块 App：自动看到同一绑定。
2. 模块 App 持续前台期间，在内置设置修改其他键（如 Q 上滑=复制），返回模块 App，无需强停即可刷新。
3. 在模块 App 修改但不保存某个按键，然后从内置页面保存新配置：收到同步冲突提醒，不能丢失尚未保存的编辑。
4. 独立模块 App 保存后，内置页面读取应一致，反向修改后再观察 App 一致。
5. 按钮“从微信输入法读取最新配置”可主动补拉；若输入法停止，提示先启动键盘。
6. 检查 v1.12.0 下已经配置的 L 键上/下滑、其它字母、九宫格、自定义文本与标签没有被重置。

自动化：`./gradlew --no-daemon --stacktrace clean testDebugUnitTest lintRelease assembleRelease`

## 版本、发布与回滚
- v1.12.1-test1 / versionCode 67，原永久签名候选 APK。
- **仅测试分支和 Draft PR，不合并 main，不覆盖正式 v1.12.0 GitHub Release。**
- 如测试异常，可在有 TXT 备份和可保留数据的降级方式下回到 v1.12.0；Android 可能禁止直接降级。
