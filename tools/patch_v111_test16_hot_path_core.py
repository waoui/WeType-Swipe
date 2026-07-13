from pathlib import Path
import runpy

runpy.run_path("tools/patch_v111_test15_label_and_baseline.py", run_name="__main__")

p = Path("app/src/main/java/com/rww/wetypeswipe/MainHook.java")
s = p.read_text(encoding="utf-8")

def r(old, new, name):
    global s
    if s.count(old) != 1:
        raise RuntimeError(name)
    s = s.replace(old, new, 1)

r("    private volatile long nativeSingleKeyLastDrawUptimeMs;",
  "    private final ConcurrentHashMap<Object, String> nativeSingleKeyLabelCache = new ConcurrentHashMap<>();",
  "cache field")

r('''            View activeKeyboard = nativeSingleKeyActiveKeyboardRef.get();
            if (activeKeyboard == keyboard
                    && SystemClock.uptimeMillis() - nativeSingleKeyLastDrawUptimeMs < 250L) {
                return;
            }''',
  '''            if (nativeSingleKeyActiveKeyboardRef.get() == keyboard) return;''',
  "fallback gate")

r('''        if (previous != keyboard) nativeSingleKeyActiveKeyboardRef = new WeakReference<>(keyboard);
        nativeSingleKeyLastDrawUptimeMs = SystemClock.uptimeMillis();''',
  '''        if (previous != keyboard) {
            nativeSingleKeyActiveKeyboardRef = new WeakReference<>(keyboard);
            nativeSingleKeyLabelCache.clear();
        }''',
  "keyboard cache reset")

old = '''        Config config = cachedConfig;
        if (config == null || !config.hasAnyBinding()) return;

        String id;
        try { id = String.valueOf(model); }
        catch (Throwable ignored) { id = null; }
        String key = keyFromNativeLayoutId(id);
        if (key == null) {
            Object value = invoke(model, "K");
            key = keyFromNativeLayoutId(value == null ? null : String.valueOf(value));
        }
        if (key == null) return;

        char value = key.charAt(0);
        boolean t9 = value >= '1' && value <= '9';
        int action = config.actionFor(key, t9);
        if (action == Config.ACTION_NONE || action == Config.ACTION_DISABLE) return;'''
new = '''        String label = nativeSingleKeyLabelCache.get(model);
        if (label == null) {
            Config config = cachedConfig;
            if (config == null || !config.hasAnyBinding()) return;
            String id;
            try { id = String.valueOf(model); }
            catch (Throwable ignored) { id = null; }
            String key = keyFromNativeLayoutId(id);
            if (key == null) {
                Object value = invoke(model, "K");
                key = keyFromNativeLayoutId(value == null ? null : String.valueOf(value));
            }
            if (key == null) label = "";
            else {
                char value = key.charAt(0);
                boolean t9 = value >= '1' && value <= '9';
                int action = config.actionFor(key, t9);
                label = action == Config.ACTION_NONE || action == Config.ACTION_DISABLE
                        ? "" : shortActionLabel(action);
            }
            nativeSingleKeyLabelCache.put(model, label);
        }
        if (label.isEmpty()) return;'''
r(old, new, "label cache hot path")

r('''        drawKeyFunctionText((Canvas) canvasValue, shortActionLabel(action),
                drawRect.exactCenterX(), baseline);''',
  '''        drawKeyFunctionText((Canvas) canvasValue, label,
                drawRect.exactCenterX(), baseline);''',
  "cached label draw")

p.write_text(s, encoding="utf-8")
print("test16 core hot-path cache applied")
