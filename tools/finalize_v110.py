from pathlib import Path
import glob
from textwrap import dedent

ROOT = Path('.')
HOOK = ROOT / 'app/src/main/java/com/rww/wetypeswipe/MainHook.java'
ACTIVITY = ROOT / 'app/src/main/java/com/rww/wetypeswipe/MainActivity.java'
BUILD = ROOT / 'app/build.gradle.kts'
README = ROOT / 'README.md'


def replace_exact(path: Path, old: str, new: str, count: int = 1) -> None:
    text = path.read_text(encoding='utf-8')
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f'{path}: expected {count} matches, found {actual}: {old[:160]!r}')
    path.write_text(text.replace(old, new, count), encoding='utf-8')


def remove_range(text: str, start_marker: str, end_marker: str) -> str:
    start = text.find(start_marker)
    if start < 0:
        raise RuntimeError(f'missing start marker: {start_marker}')
    end = text.find(end_marker, start)
    if end < 0:
        raise RuntimeError(f'missing end marker: {end_marker}')
    return text[:start] + text[end:]


exec(
    compile(
        (ROOT / 'tools/patch_v110_test11.py').read_text(encoding='utf-8'),
        'tools/patch_v110_test11.py',
        'exec',
    )
)

replace_exact(BUILD, 'versionName = "1.10.0-test11"', 'versionName = "1.10.0"')
replace_exact(
    ACTIVITY,
    'v1.10.0-test11 · 横屏悬浮键盘窗口适配',
    'v1.10.0 · 原生剪贴板与快捷发送',
)
replace_exact(
    HOOK,
    'logInfo("v1.10.0-test11 entered target package");',
    'logInfo("v1.10.0 entered target package");',
)

hook = HOOK.read_text(encoding='utf-8')
for line in (
    'import android.widget.ImageView;\n',
    'import android.widget.TextView;\n',
    'import java.lang.reflect.Modifier;\n',
    '    private volatile View.OnClickListener clipboardNativeListener;\n',
    '    private volatile View.OnClickListener quickPhraseNativeListener;\n',
    '    private volatile Object clipboardNativeCallback;\n',
    '    private volatile Object quickPhraseNativeCallback;\n',
    '    private volatile WeakReference<View> clipboardListenerSourceRef = new WeakReference<>(null);\n',
    '    private volatile WeakReference<View> quickPhraseListenerSourceRef = new WeakReference<>(null);\n',
):
    hook = hook.replace(line, '')

hook = remove_range(
    hook,
    '    private void cacheNativePanelListeners(InputMethodService ime) {',
    '    private boolean invokeToolbarCommandCarrier(View root, int action) {',
)
hook = remove_range(
    hook,
    '    private boolean invokeCachedNativeCallback(InputMethodService ime, int action) {',
    '    private View findImageResourceAny(View view, int resourceId) {',
)
hook = remove_range(
    hook,
    '    private View findImageResourceAny(View view, int resourceId) {',
    '    private static View.OnClickListener readOnClickListener(View view) {',
)
hook = remove_range(
    hook,
    '    private static int imageResourceId(ImageView image) {',
    '    private static Object readNamedField(Object object, String name) {',
)
hook = remove_range(
    hook,
    '    private static String describeObjectGraph(Object root) {',
    '    private static String describeListenerFields(Object listener) {',
)
hook = remove_range(
    hook,
    '    private static String describeListenerFields(Object listener) {',
    '    private static boolean isParagraphAction(int action) {',
)
hook = hook.replace('        logInfo("toolbar command carrier cached");\n', '')
HOOK.write_text(hook, encoding='utf-8')

readme = README.read_text(encoding='utf-8')
readme = readme.replace('> 当前稳定版本：v1.9.4', '> 当前稳定版本：v1.10.0')
if '## v1.10.0' not in readme:
    readme += dedent('''

    ## v1.10.0

    - 新增“剪贴板”下滑动作，可直接打开微信输入法原生剪贴板历史。
    - 新增“快捷发送”下滑动作，可直接打开微信输入法原生快捷发送/常用语面板。
    - 两项功能无需在输入法工具栏中显示对应按钮。
    - 支持 26 键、九宫格、横屏及横屏悬浮键盘。
    - 优化触摸热路径、反射成员缓存和窗口切换后的缓存失效恢复。
    ''').lstrip('\n')
README.write_text(readme, encoding='utf-8')

release_notes = dedent('''\
# 微信输入法下滑快捷键 v1.10.0

适用于安卓版微信输入法的 LSPosed 模块，支持 26 键和九宫格按键下滑快捷操作。

## 新增功能

- **剪贴板**：直接打开微信输入法原生剪贴板历史面板。
- **快捷发送**：直接打开微信输入法原生快捷发送/常用语面板。
- 两项功能不需要在输入法工具栏中显示对应按钮。
- 支持竖屏、横屏、横屏悬浮键盘模式。

## 性能与稳定性

- 移除普通按键过程中的工具栏 View 树扫描。
- 缓存原生工具栏命令载体及反射成员，仅在窗口或输入法实例变化时重新解析。
- 移除键位识别热路径中的正则处理。
- 增加工具栏窗口切换、横竖屏和悬浮键盘模式的缓存失效保护。
- 保留失败日志，减少正常输入与成功触发时的日志写入。

## 兼容性

- 适配安卓版微信输入法。
- 需要 LSPosed 环境。
''')
(ROOT / 'RELEASE_NOTES_v1.10.0.md').write_text(release_notes, encoding='utf-8')

publish_workflow = dedent('''\
name: Publish v1.10.0

on:
  push:
    branches: [main]
    paths:
      - "app/**"
      - "RELEASE_NOTES_v1.10.0.md"
      - ".github/workflows/publish-v1.10.0.yml"
  workflow_dispatch:

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: "17"

      - uses: gradle/actions/setup-gradle@v4
        with:
          gradle-version: "8.9"

      - name: Restore signing certificate
        shell: bash
        env:
          SIGNING_KEY_BASE64: ${{ secrets.SIGNING_KEY_BASE64 }}
        run: |
          test -n "$SIGNING_KEY_BASE64"
          printf '%s' "$SIGNING_KEY_BASE64" | base64 --decode > signing.jks

      - name: Build signed release APK
        shell: bash
        env:
          SIGNING_STORE_FILE: ${{ github.workspace }}/signing.jks
          SIGNING_STORE_PASSWORD: ${{ secrets.SIGNING_STORE_PASSWORD }}
          SIGNING_KEY_ALIAS: ${{ secrets.SIGNING_KEY_ALIAS }}
          SIGNING_KEY_PASSWORD: ${{ secrets.SIGNING_KEY_PASSWORD }}
        run: |
          gradle --no-daemon clean assembleRelease
          mkdir -p output
          cp app/build/outputs/apk/release/app-release.apk \\
            output/WeType_Swipe_LSPosed_v1.10.0.apk
          sha256sum output/WeType_Swipe_LSPosed_v1.10.0.apk \\
            | tee output/WeType_Swipe_LSPosed_v1.10.0.apk.sha256

      - name: Create or update GitHub Release
        shell: bash
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          if gh release view v1.10.0 >/dev/null 2>&1; then
            gh release upload v1.10.0 \\
              output/WeType_Swipe_LSPosed_v1.10.0.apk \\
              output/WeType_Swipe_LSPosed_v1.10.0.apk.sha256 \\
              --clobber
          else
            gh release create v1.10.0 \\
              output/WeType_Swipe_LSPosed_v1.10.0.apk \\
              output/WeType_Swipe_LSPosed_v1.10.0.apk.sha256 \\
              --target "${GITHUB_SHA}" \\
              --title "WeType Swipe v1.10.0" \\
              --notes-file RELEASE_NOTES_v1.10.0.md
          fi

      - if: always()
        run: rm -f signing.jks
''')
workflow_dir = ROOT / '.github/workflows'
workflow_dir.mkdir(parents=True, exist_ok=True)
(workflow_dir / 'publish-v1.10.0.yml').write_text(publish_workflow, encoding='utf-8')

for pattern in (
    '.github/workflows/test-v1.10.0*.yml',
    '.github/workflows/prepare-v1.10.0.yml',
    '.github/workflows/finalize-v1.10.0.yml',
    'tools/patch_v110_test*.py',
    'tools/finalize_v110.py',
):
    for item in glob.glob(pattern):
        path = Path(item)
        if path.is_file():
            path.unlink()

print('v1.10.0 production source finalized')
