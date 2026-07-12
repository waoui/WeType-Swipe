from pathlib import Path

# Apply the existing v1.10.0-test1 feature patch first.
exec(compile(Path("tools/patch_v110_test.py").read_text(encoding="utf-8"), "tools/patch_v110_test.py", "exec"))


def replace(path: str, old: str, new: str, count: int = 1) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{path}: expected {count} matches, found {actual}: {old[:140]!r}")
    file.write_text(text.replace(old, new, count), encoding="utf-8")


hook = "app/src/main/java/com/rww/wetypeswipe/MainHook.java"
replace(hook, "import android.widget.TextView;\n", "import android.widget.ImageView;\nimport android.widget.TextView;\n")
replace(hook, "import java.lang.reflect.Method;\n", "import java.lang.reflect.Field;\nimport java.lang.reflect.Method;\n")
replace(hook, 'logInfo("v1.10.0-test1 entered target package");', 'logInfo("v1.10.0-test4 entered target package");')

replace(
    hook,
    '''        String[] targets = action == Config.ACTION_OPEN_CLIPBOARD
                ? new String[]{"剪贴板", "clipboard", "clip_board"}
                : new String[]{"快捷发送", "常用语", "快捷语", "quickphrase", "quick_phrase", "commonphrase", "common_phrase"};

        if (clickMatchingView(root, targets)) return true;
''',
    '''        int iconResource = action == Config.ACTION_OPEN_CLIPBOARD
                ? 2131231369
                : 2131231376;
        if (clickImageResource(root, iconResource)) {
            logInfo(Config.actionName(action) + " opened by native icon resource " + iconResource);
            return true;
        }

        String[] targets = action == Config.ACTION_OPEN_CLIPBOARD
                ? new String[]{"剪贴板", "clipboard", "clip_board"}
                : new String[]{"快捷发送", "常用语", "快捷语", "quickphrase", "quick_phrase", "commonphrase", "common_phrase"};

        if (clickMatchingView(root, targets)) return true;
''',
)

helpers = r'''
    private boolean clickImageResource(View root, int resourceId) {
        View icon = findImageResource(root, resourceId);
        if (icon == null) return false;
        View clickable = nearestClickable(icon);
        if (clickable == null) return false;
        try {
            boolean result = clickable.performClick();
            logInfo("native icon click resource=" + resourceId
                    + " icon=" + icon.getClass().getName()
                    + " parent=" + clickable.getClass().getName()
                    + " result=" + result);
            return result;
        } catch (Throwable throwable) {
            logError("native icon click failed resource=" + resourceId, throwable);
            return false;
        }
    }

    private View findImageResource(View view, int resourceId) {
        if (view == null || view.getVisibility() != View.VISIBLE || !view.isShown()) return null;
        if (view instanceof ImageView && imageResourceId((ImageView) view) == resourceId) return view;
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int index = 0; index < group.getChildCount(); index++) {
                View result = findImageResource(group.getChildAt(index), resourceId);
                if (result != null) return result;
            }
        }
        return null;
    }

    private static int imageResourceId(ImageView image) {
        if (image == null) return 0;
        try {
            Field field = ImageView.class.getDeclaredField("mResource");
            field.setAccessible(true);
            return field.getInt(image);
        } catch (Throwable ignored) {
            return 0;
        }
    }

'''
replace(hook, "    private boolean clickMatchingView(View root, String[] tokens) {", helpers + "    private boolean clickMatchingView(View root, String[] tokens) {")

replace(
    "app/build.gradle.kts",
    'versionName = "1.10.0-test1"',
    'versionName = "1.10.0-test4"',
)
replace(
    "app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
    'v1.10.0 测试版 · 原生剪贴板与快捷发送',
    'v1.10.0-test4 · 原生图标定向调用',
)

print("v1.10.0-test4 resource-based panel patch applied")
