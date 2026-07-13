from pathlib import Path
import runpy

runpy.run_path("tools/patch_v111_test8.py", run_name="__main__")


def replace(path: str, old: str, new: str, count: int = 1) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{path}: expected {count} matches, found {actual}: {old[:180]!r}")
    file.write_text(text.replace(old, new, count), encoding="utf-8")


hook = "app/src/main/java/com/rww/wetypeswipe/MainHook.java"

replace(hook,
        '            logInfo("v1.11.0-test8 entered target package");',
        '            logInfo("v1.11.0-test9 entered target package");')

replace(hook,
'''                float center = inferVisualKeyCenter(centers, keys, index, value, spacing);
                RectF nativeRect = nativeKeyRectAt(keyboard, center, sampleY);
                if (nativeRect != null) {
                    float baseline = nativeRect.bottom
                            - Math.max(dp(keyboard, 3), nativeRect.height() * 0.16f);
                    keyOutput.add(new KeyLabelBounds(nativeRect.left, nativeRect.top,
                            nativeRect.right, nativeRect.bottom, baseline, true));
                } else {
                    keyOutput.add(new KeyLabelBounds(center - inferredWidth * 0.5f, rowTop,
                            center + inferredWidth * 0.5f, rowBottom,
                            fallbackBaseline, false));
                }
''',
'''                float center = inferVisualKeyCenter(centers, keys, index, value, spacing);
                boolean outerEdgeKey = index == 0 || index == keys.length() - 1;
                // Edge keys commonly expose an enlarged touch Rect that reaches into
                // the keyboard gutter. That is not the visible keycap. Use the row's
                // neighbour-derived visual lattice for those keys instead.
                RectF nativeRect = outerEdgeKey ? null : nativeKeyRectAt(keyboard, center, sampleY);
                if (nativeRect != null) {
                    float baseline = nativeRect.bottom
                            - Math.max(dp(keyboard, 3), nativeRect.height() * 0.16f);
                    keyOutput.add(new KeyLabelBounds(nativeRect.left, nativeRect.top,
                            nativeRect.right, nativeRect.bottom, baseline, true));
                } else {
                    keyOutput.add(new KeyLabelBounds(center - inferredWidth * 0.5f, rowTop,
                            center + inferredWidth * 0.5f, rowBottom,
                            fallbackBaseline, false));
                }
                if (outerEdgeKey && "a".equals(key)) {
                    logInfo("key-label geometry key=a source=neighbor-grid measured="
                            + value + " resolved=" + center + " spacing=" + spacing
                            + " width=" + inferredWidth);
                }
''')

replace("app/build.gradle.kts", "versionCode = 26", "versionCode = 27")
replace("app/build.gradle.kts", 'versionName = "1.11.0-test8"', 'versionName = "1.11.0-test9"')
replace("app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
        'v1.11.0-test8 · 原生键帽边界优先',
        'v1.11.0-test9 · 边缘键视觉中心推算')

print("v1.11.0-test9 edge-key visual-center patch applied")
