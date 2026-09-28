from pathlib import Path


def replace(path, old, new, count=1):
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"pattern not found in {path}: {old[:160]!r}")
    text = text.replace(old, new, count)
    p.write_text(text, encoding="utf-8")


# Test version. versionCode 56 was used by v1.11.9-test1 and must not be reused.
replace("gradle.properties",
        "VERSION_CODE=56\nVERSION_NAME=1.11.9-test1",
        "VERSION_CODE=57\nVERSION_NAME=1.11.9-test2")

for path in [
    "app/src/main/java/com/rww/wetypeswipe/MainHook.java",
    "app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
    "app/src/main/java/com/rww/wetypeswipe/EmbeddedSettingsUi.java",
]:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    text = text.replace("v1.11.9-test1", "v1.11.9-test2")
    p.write_text(text, encoding="utf-8")

main_hook = "app/src/main/java/com/rww/wetypeswipe/MainHook.java"

# Track the last live mode. A mode transition invalidates the native single-key
# paint signature even when WeType keeps the same 26-key View instance alive.
replace(main_hook,
        "    private volatile long nativeSingleKeyPaintSignature = Long.MIN_VALUE;\n",
        "    private volatile long nativeSingleKeyPaintSignature = Long.MIN_VALUE;\n"
        "    private volatile int lastResolvedNightMode = Configuration.UI_MODE_NIGHT_UNDEFINED;\n")

# Native single-key rendering used the keyboard View's potentially stale Resources.
# Build the signature from the live Application/IME mode instead.
replace(main_hook,
        "        int night = keyboard.getResources().getConfiguration().uiMode\n"
        "                & Configuration.UI_MODE_NIGHT_MASK;\n"
        "        int density = Float.floatToIntBits(\n"
        "                keyboard.getResources().getDisplayMetrics().scaledDensity);\n"
        "        int keyHeight = Math.max(1, drawRect.height());\n"
        "        long signature = (((long) keyboard.getWidth()) << 40)\n"
        "                ^ (((long) keyboard.getHeight()) << 16)\n"
        "                ^ (((long) keyHeight) << 4)\n"
        "                ^ (((long) night) << 2)\n"
        "                ^ (density & 0xffffffffL);\n",
        "        int night = resolveLiveNightMode(keyboard);\n"
        "        int density = Float.floatToIntBits(\n"
        "                keyboard.getResources().getDisplayMetrics().scaledDensity);\n"
        "        int keyHeight = Math.max(1, drawRect.height());\n"
        "        long signature = KeyboardThemeState.paintSignature(\n"
        "                keyboard.getWidth(), keyboard.getHeight(), keyHeight, density, night);\n")

# Fallback/full-keyboard rendering must use the same live source.
replace(main_hook,
        "        boolean night = (keyboard.getResources().getConfiguration().uiMode\n"
        "                & Configuration.UI_MODE_NIGHT_MASK) == Configuration.UI_MODE_NIGHT_YES;\n",
        "        boolean night = KeyboardThemeState.isNight(resolveLiveNightMode(keyboard));\n")

marker = "    private void prepareKeyboardLabelPaint(View keyboard) {\n"
helper = '''    private int resolveLiveNightMode(View keyboard) {
        if (keyboard == null) return Configuration.UI_MODE_NIGHT_UNDEFINED;

        int keyboardUiMode = Configuration.UI_MODE_NIGHT_UNDEFINED;
        int applicationUiMode = Configuration.UI_MODE_NIGHT_UNDEFINED;
        int imeUiMode = Configuration.UI_MODE_NIGHT_UNDEFINED;

        try {
            keyboardUiMode = keyboard.getResources().getConfiguration().uiMode;
        } catch (Throwable ignored) {}

        try {
            Context application = keyboard.getContext().getApplicationContext();
            if (application != null) {
                applicationUiMode = application.getResources().getConfiguration().uiMode;
            }
        } catch (Throwable ignored) {}

        InputMethodService ime = imeRef.get();
        if (ime != null) {
            try {
                Context application = ime.getApplicationContext();
                if (application != null) {
                    applicationUiMode = application.getResources().getConfiguration().uiMode;
                }
            } catch (Throwable ignored) {}
            try {
                imeUiMode = ime.getResources().getConfiguration().uiMode;
            } catch (Throwable ignored) {}
        }

        int resolved = KeyboardThemeState.resolveNightMode(
                keyboardUiMode, applicationUiMode, imeUiMode);
        int previous = lastResolvedNightMode;
        if (resolved != previous) {
            lastResolvedNightMode = resolved;
            nativeSingleKeyPaintSignature = Long.MIN_VALUE;
            View activeKeyboard = nativeSingleKeyActiveKeyboardRef.get();
            if (activeKeyboard != null && activeKeyboard != keyboard) activeKeyboard.postInvalidate();
            keyboard.postInvalidate();
            if (previous != Configuration.UI_MODE_NIGHT_UNDEFINED) {
                logInfo("keyboard label theme refreshed: " + previous + " -> " + resolved);
            }
        }
        return resolved;
    }

'''
replace(main_hook, marker, helper + marker)

# Keep the package-entry log accurate for the test build.
p = Path(main_hook)
text = p.read_text(encoding="utf-8")
text = text.replace(
    "phase-1 architecture refactor enabled",
    "phase-1 refactor + live dark-mode refresh enabled")
p.write_text(text, encoding="utf-8")
