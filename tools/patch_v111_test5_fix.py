from pathlib import Path
import runpy

runpy.run_path("tools/patch_v111_test5.py", run_name="__main__")

path = Path("app/src/main/java/com/rww/wetypeswipe/MainHook.java")
text = path.read_text(encoding="utf-8")
old = '''        keyboardLabelLayoutSignature = signature;
        if (keyboardLabelGeometryBuilding) return;
        keyboardLabelGeometryBuilding = true;
        keyboard.post(() -> rebuildKeyboardLabelGeometry(keyboard, signature));
'''
new = '''        keyboardLabelLayoutSignature = signature;
        if (keyboardLabelGeometryBuilding) return;
        keyboardLabelGeometryBuilding = true;
        final String capturedSignature = signature;
        keyboard.post(() -> rebuildKeyboardLabelGeometry(keyboard, capturedSignature));
'''
if text.count(old) != 1:
    raise RuntimeError("test5 lambda marker not found")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("v1.11.0-test5 lambda capture fix applied")
