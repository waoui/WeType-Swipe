from pathlib import Path
import atexit
import runpy
import sys

# Existing test8 workflow invokes patch_v111_test8_fix.py, which in turn runs
# this script. Register the test9 post-step for that exact entry point so the
# proven signing/build workflow can be reused without changing its secrets.
if sys.argv and sys.argv[0].endswith("patch_v111_test8_fix.py"):
    atexit.register(lambda: runpy.run_path("tools/patch_v111_test9_after.py", run_name="__main__"))

runpy.run_path("tools/patch_v111_test6.py", run_name="__main__")


def replace(path: str, old: str, new: str, count: int = 1) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{path}: expected {count} matches, found {actual}: {old[:180]!r}")
    file.write_text(text.replace(old, new, count), encoding="utf-8")


hook = "app/src/main/java/com/rww/wetypeswipe/MainHook.java"

replace(hook,
        '            logInfo("v1.11.0-test6 entered target package");',
        '            logInfo("v1.11.0-test7 entered target package");')

# Pass the current keyboard View to the row renderer so edge-key labels can be
# corrected relative to the real keyboard width and density.
replace(hook,
'''        drawQwertyRow(canvas, config, "qwertyuiop", firstBaseline);
         drawQwertyRow(canvas, config, "asdfghjkl", secondBaseline);
         drawQwertyRow(canvas, config, "zxcvbnm", thirdBaseline);
''',
'''        drawQwertyRow(keyboard, canvas, config, "qwertyuiop", firstBaseline);
         drawQwertyRow(keyboard, canvas, config, "asdfghjkl", secondBaseline);
         drawQwertyRow(keyboard, canvas, config, "zxcvbnm", thirdBaseline);
''')

replace(hook,
'''    private void drawQwertyRow(Canvas canvas, Config config, String keys, float baseline) {
         Map<String, List<Float>> centers = keyboardLabelCenters;
         if (centers == null || centers.isEmpty()) return;
         for (int index = 0; index < keys.length(); index++) {
             String key = String.valueOf(keys.charAt(index));
             int action = config.actionFor(key, false);
             if (action == Config.ACTION_NONE) continue;
             List<Float> positions = centers.get(key);
             if (positions == null) continue;
             for (Float x : positions) {
                 if (x != null) drawKeyFunctionText(canvas, shortActionLabel(action), x, baseline);
             }
         }
     }
''',
'''    private void drawQwertyRow(View keyboard, Canvas canvas, Config config,
                                 String keys, float baseline) {
         Map<String, List<Float>> centers = keyboardLabelCenters;
         if (centers == null || centers.isEmpty()) return;
         int width = Math.max(1, keyboard.getWidth());
         float leftEdgeCorrection = Math.max(dp(keyboard, 5), Math.min(dp(keyboard, 9), width * 0.012f));
         for (int index = 0; index < keys.length(); index++) {
             String key = String.valueOf(keys.charAt(index));
             int action = config.actionFor(key, false);
             if (action == Config.ACTION_NONE || action == Config.ACTION_DISABLE) continue;
             List<Float> positions = centers.get(key);
             if (positions == null) continue;
             for (Float position : positions) {
                 if (position == null) continue;
                 float x = position;
                 // The hit-test region of the leftmost A key extends into the
                 // keyboard edge gutter. Its geometric center is therefore left
                 // of the visible keycap center. Correct only that edge instance.
                 if ("a".equals(key) && x < width * 0.18f) {
                     x += leftEdgeCorrection;
                 }
                 drawKeyFunctionText(canvas, shortActionLabel(action), x, baseline);
             }
         }
     }
''')

# A disabled binding remains functional, but does not need a persistent label.
replace(hook,
        '            case Config.ACTION_DISABLE: return "禁用";',
        '            case Config.ACTION_DISABLE: return "";')

# Apply the same visual policy to T9 labels.
replace(hook,
        '            if (action == Config.ACTION_NONE) continue;\n            int zeroBased = digit - 1;',
        '            if (action == Config.ACTION_NONE || action == Config.ACTION_DISABLE) continue;\n            int zeroBased = digit - 1;',
        count=1)

replace("app/build.gradle.kts", "versionCode = 24", "versionCode = 25")
replace("app/build.gradle.kts", 'versionName = "1.11.0-test6"', 'versionName = "1.11.0-test7"')
replace("app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
        'v1.11.0-test6 · 按键文字位置优化',
        'v1.11.0-test7 · 边缘按键位置修正')

print("v1.11.0-test7 edge-key label correction patch applied")
