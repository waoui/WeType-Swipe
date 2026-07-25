#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    ROOT / "app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
    "v1.11.5-test1 · 新增全文导航与跨行选择",
    "v1.11.5 · 新增全文导航与跨行选择",
)
replace_once(
    ROOT / "app/src/main/java/com/rww/wetypeswipe/MainHook.java",
    'logInfo("v1.11.5-test1 entered target package; document navigation actions enabled");',
    'logInfo("v1.11.5 entered target package; document navigation actions enabled");',
)
replace_once(
    ROOT / "gradle.properties",
    "VERSION_NAME=1.11.5-test1",
    "VERSION_NAME=1.11.5",
)

replace_once(
    ROOT / "CHANGELOG.md",
    "# 更新记录\n\n",
    """# 更新记录

## v1.11.5

- 新增“文首”“文尾”“选至文首”“选至文尾”4 个全文级下滑动作
- 新动作编号追加为 16–19，原有 0–15 编号和用户配置保持不变
- 全文级动作可跨越多行和多个段落；原“段首／段尾”动作语义保持不变
- 已有选区执行“选至文首／文尾”时保留另一侧边界
- 文尾类动作仅在目标编辑器返回完整文本范围时执行，避免把局部上下文误判为全文
- 保持数字、符号、手写键盘、密码输入框和既有快捷动作隔离逻辑不变

""",
)

readme = ROOT / "README.md"
replace_once(readme, "当前稳定版本：**v1.11.4**", "当前稳定版本：**v1.11.5**")
replace_once(
    readme,
    "- 选择当前位置到段首、段尾\n",
    "- 选择当前位置到段首、段尾\n- 移动到整篇文本的文首、文尾\n- 选择当前位置到整篇文本的文首、文尾\n",
)
replace_once(
    readme,
    """## v1.11.4 更新内容

- 新增“撤销”和“重做”下滑动作，26 键与九宫格均可绑定。
- 使用 Android 标准编辑器撤销／重做指令，不保存输入内容，也不维护私有撤销栈。
- 触发前结束当前输入法组词状态，再由目标 App 的输入框执行撤销或重做。
- 中文输入可能按“中文 → 拼音 → 空白”的顺序撤销，这是目标编辑器对组词和上屏记录为两个步骤的正常表现。
- 保持数字、符号、手写键盘和密码输入框的隔离逻辑不变。
- 保持 v1.11.3 的原生剪贴板、快捷发送和标签兼容修复不变。

完整变更请查看 [v1.11.4 Release](https://github.com/waoui/WeType-Swipe/releases/tag/v1.11.4) 和 [更新记录](CHANGELOG.md)。
""",
    """## v1.11.5 更新内容

- 新增“文首”“文尾”“选至文首”“选至文尾”4 个全文级动作，26 键与九宫格均可绑定。
- 全文级动作可跨越多行和多个段落；原有“段首、段尾、选至段首、选至段尾”继续只处理当前段落。
- 对已有选区执行“选至文首”或“选至文尾”时，会保留选区另一侧边界。
- 文尾类动作只在目标编辑器能够返回完整文本范围时执行，避免错误选择到局部上下文末尾。
- 新动作编号追加为 16–19，不改变既有动作编号、默认键位和用户配置。
- 保持撤销／重做、原生剪贴板、快捷发送、数字／符号页与手写键盘隔离逻辑不变。

完整变更请查看 [v1.11.5 Release](https://github.com/waoui/WeType-Swipe/releases/tag/v1.11.5) 和 [更新记录](CHANGELOG.md)。
""",
)

(ROOT / "RELEASE_NOTES_v1.11.5.md").write_text("""# 微信输入法下滑快捷键 v1.11.5

本版本新增独立的全文级导航与选择动作，解决多行文本中只能在当前段落内移动或选择的问题。

## 新增功能

- **文首**：将光标移动到整个编辑文本最前面。
- **文尾**：将光标移动到整个编辑文本最后面。
- **选至文首**：从当前光标或已有选区右边界，跨行选择到全文开头。
- **选至文尾**：从当前光标或已有选区左边界，跨行选择到全文结尾。
- 26 键与九宫格均可绑定以上 4 个动作，并支持自动标签、自定义标签和隐藏标签。

## 行为与兼容说明

- 原有“段首、段尾、选至段首、选至段尾”继续以换行符划分当前段落，语义不变。
- 新动作编号为 16–19，原有 0–15 编号、默认键位和历史用户配置保持兼容。
- 对已有选区使用“选至文首／文尾”时，会保留选区另一侧边界。
- “文尾”和“选至文尾”仅在目标编辑器返回完整文本范围后执行；自绘编辑器拒绝返回全文时会安全失败，不会把局部上下文末尾当成全文末尾。
- 模块不保存、上传或记录用户输入内容。

## 兼容性

- Android 8.0 及以上
- LSPosed
- 微信输入法 3.5.0、3.5.2
- 本次真机验收环境：Android 16、微信输入法 3.5.2

## 发布验证

- 26 键与九宫格新增动作绑定、标签显示和配置同步真机验证通过
- 三行以上文本的文首／文尾跨行移动验证通过
- 选至文首／选至文尾跨行选择及已有选区扩展验证通过
- 原段落级动作语义验证通过
- 空文本、单行、末尾换行和较长文本未发现异常
- 数字、符号、手写键盘和密码输入框隔离验证通过
- 复制、剪切、粘贴、全选、撤销、重做、剪贴板和快捷发送未发现回归
- 单元测试、Android Lint、Debug/Release 构建和永久签名校验通过

## 升级说明

可直接覆盖安装 v1.11.4。升级后建议强制停止并重新启动微信输入法；原有键位映射、自定义标签和开关配置保持不变。
""", encoding="utf-8")

# Generated source must restore the normal CI and remove every one-off generator.
(ROOT / ".github/workflows/ci.yml").write_text("""name: 持续集成

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  verify:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: 检出源码
        uses: actions/checkout@v4

      - name: 配置 Java
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: "17"

      - name: 配置 Gradle 缓存
        uses: gradle/actions/setup-gradle@v4

      - name: 单元测试、Lint 与 Debug 构建
        shell: bash
        run: ./gradlew --no-daemon --stacktrace testDebugUnitTest lintDebug assembleDebug
""", encoding="utf-8")

for relative in (
    ".github/workflows/finalize-v1.11.5.yml",
    "tools/patch_document_navigation_test.py",
    "tools/finalize_document_navigation_release.py",
):
    path = ROOT / relative
    if path.exists():
        path.unlink()

print("Finalized v1.11.5 source and removed one-off generators")
