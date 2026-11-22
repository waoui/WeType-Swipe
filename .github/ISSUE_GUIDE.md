# Issues 分类与发布规范

本仓库将 **Issues 留给使用者反馈**，**GitHub Releases 留给正式版本**，Pull Requests 仅用于可合并的代码变更。

## 现有历史记录如何查找

- [用户反馈（含已关闭）](https://github.com/waoui/WeType-Swipe/issues?q=is%3Aissue+label%3Auser-feedback)
- [尚未解决的反馈](https://github.com/waoui/WeType-Swipe/issues?q=is%3Aissue+is%3Aopen+label%3Auser-feedback)
- [已解决的反馈](https://github.com/waoui/WeType-Swipe/issues?q=is%3Aissue+is%3Aclosed+label%3Auser-feedback)
- [早期发布／源码构建触发记录](https://github.com/waoui/WeType-Swipe/issues?q=is%3Aissue+label%3Arelease-automation)
- [GitHub Releases](https://github.com/waoui/WeType-Swipe/releases)

历史 Issues 不删除、不修改原报告正文，只补分类标签以便检索。已关闭的发布记录不是用户反馈；后续不会再以 Issue 作为发布触发工具。

## 分类规则

| 标签 | 用途 |
| --- | --- |
| `user-feedback` | 来自用户的缺陷、兼容性反馈和功能建议 |
| `bug` | 已有功能失败、界面异常、错误触发或兼容性问题 |
| `enhancement` | 新动作、新键盘支持、体验改进 |
| `release-automation` | 早期自动发布或源码构建的历史记录（仅归档） |

一个反馈可同时拥有 `user-feedback` 和 `bug`/`enhancement`。状态通过 GitHub Open / Closed 管理，关闭时写明解决版本或不实施的理由。切勿仅凭版本号相近就把未解决的反馈关闭。

## 今后发布正式版

1. 在功能分支验证全部改动，并由 PR 合并到 `main`。
2. 同步更新 `gradle.properties` 的 `VERSION_NAME`、`VERSION_CODE` 与 `RELEASE_NOTES_vX.Y.Z.md`。
3. 前往仓库 **Actions → 构建并发布正式版 → Run workflow**，选择 `main`，输入版本号（如 `1.14.0`，不含 `v`）。
4. Workflow 检出 `main`，核验版本和 Release Notes，运行单元测试／Lint／Release 构建，使用正式证书签名，上传 APK、源码 ZIP 和 SHA256 到 **GitHub Releases**。
5. 构建失败只查看 Actions 日志，修复后重试；**不再创建 `Publish v... final` Issue／PR**。

这样发布动作不会污染 Open/Closed Issues，发布记录集中在 Releases 和 Actions 内。

## 回滚

如果新发布入口有问题，可从提交历史恢复旧版 `.github/workflows/release.yml`，或在修复后的新分支重新提交 Workflow；仓库历史 Release、Issue 与分支不受影响。正式签名 Secret 不改动。
