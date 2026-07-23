#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one match in {path}, found {count}: {old[:80]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


hook = ROOT / "app/src/main/java/com/rww/wetypeswipe/MainHook.java"

replace_once(
    hook,
    """        ensureKeyboardLabelDrawHook(view.getClass(), view);
        if (event.getActionMasked() == MotionEvent.ACTION_DOWN && !targetCacheLoaded) {""",
    """        if (isHandwritingContext(view)) {
            tracker.clear(view);
            view.post(() -> hideKeyboardHint(0L));
            return chain.proceed();
        }

        ensureKeyboardLabelDrawHook(view.getClass(), view);
        if (event.getActionMasked() == MotionEvent.ACTION_DOWN && !targetCacheLoaded) {""",
)

replace_once(
    hook,
    """        if (keyboard == null || drawRect == null || drawRect.isEmpty()) return;

        View previous = nativeSingleKeyActiveKeyboardRef.get();""",
    """        if (keyboard == null || drawRect == null || drawRect.isEmpty()) return;
        if (isHandwritingContext(keyboard)) {
            nativeSingleKeyLabelCache.remove(model);
            return;
        }

        View previous = nativeSingleKeyActiveKeyboardRef.get();""",
)

replace_once(
    hook,
    """    private void drawKeyboardFunctionLabels(View keyboard, Canvas canvas) {
        if (keyboard == null || canvas == null || keyboard.getWidth() <= 0 || keyboard.getHeight() <= 0) return;
        Config config = cachedConfig;""",
    """    private void drawKeyboardFunctionLabels(View keyboard, Canvas canvas) {
        if (keyboard == null || canvas == null || keyboard.getWidth() <= 0 || keyboard.getHeight() <= 0) return;
        if (isHandwritingContext(keyboard)) return;
        Config config = cachedConfig;""",
)

replace_once(
    hook,
    """    private static Class<?> findKeyboardBase(Class<?> type) {
        for (int i = 0; type != null && i < 12; i++, type = type.getSuperclass()) {
            if (KEYBOARD_BASE.equals(type.getName())) return type;
        }
        return null;
    }

    private Object interceptKeyboardTouch""",
    """    private static Class<?> findKeyboardBase(Class<?> type) {
        for (int i = 0; type != null && i < 12; i++, type = type.getSuperclass()) {
            if (KEYBOARD_BASE.equals(type.getName())) return type;
        }
        return null;
    }

    private static boolean isHandwritingContext(View keyboard) {
        View current = keyboard;
        for (int depth = 0; current != null && depth < 16; depth++) {
            if (KeyboardModeGuard.isHandwritingClassName(current.getClass().getName())) return true;
            Object parent = current.getParent();
            current = parent instanceof View ? (View) parent : null;
        }
        return false;
    }

    private Object interceptKeyboardTouch""",
)

guard = ROOT / "app/src/main/java/com/rww/wetypeswipe/KeyboardModeGuard.java"
guard.write_text(
    """package com.rww.wetypeswipe;

import java.util.Locale;

final class KeyboardModeGuard {
    private KeyboardModeGuard() {}

    static boolean isHandwritingClassName(String className) {
        if (className == null || className.isEmpty()) return false;
        String normalized = className.toLowerCase(Locale.ROOT);
        return normalized.contains("handwrite") || normalized.contains("hand_write");
    }
}
""",
    encoding="utf-8",
)

test = ROOT / "app/src/test/java/com/rww/wetypeswipe/KeyboardModeGuardTest.java"
test.write_text(
    """package com.rww.wetypeswipe;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public final class KeyboardModeGuardTest {
    @Test public void identifiesKnownHandwritingKeyboards() {
        assertTrue(KeyboardModeGuard.isHandwritingClassName(
                "com.tencent.wetype.plugin.hld.keyboard.selfdraw.HandWriteKeyboard"));
        assertTrue(KeyboardModeGuard.isHandwritingClassName(
                "com.tencent.wetype.plugin.hld.keyboard.selfdraw.HandWriteFullScreenKeyboard"));
        assertTrue(KeyboardModeGuard.isHandwritingClassName(
                "com.tencent.wetype.plugin.hld.keyboard.selfdraw.S27HandwriteT9Keyboard"));
        assertTrue(KeyboardModeGuard.isHandwritingClassName(
                "com.tencent.wetype.plugin.hld.keyboard.selfdraw.S28HandwriteT26Keyboard"));
        assertTrue(KeyboardModeGuard.isHandwritingClassName(
                "com.tencent.wetype.plugin.hld.handwrite.ImeHandWriteKeyboardView"));
    }

    @Test public void keepsNormalKeyboardsEnabled() {
        assertFalse(KeyboardModeGuard.isHandwritingClassName(null));
        assertFalse(KeyboardModeGuard.isHandwritingClassName(""));
        assertFalse(KeyboardModeGuard.isHandwritingClassName(
                "com.tencent.wetype.plugin.hld.keyboard.selfdraw.QwertyKeyboard"));
        assertFalse(KeyboardModeGuard.isHandwritingClassName(
                "com.tencent.wetype.plugin.hld.keyboard.selfdraw.S27T9Keyboard"));
    }
}
""",
    encoding="utf-8",
)

replace_once(
    ROOT / "CHANGELOG.md",
    "- 修复数字／符号页面错误显示 QWERTY 下滑功能标签\n",
    "- 修复数字／符号页面错误显示 QWERTY 下滑功能标签\n"
    "- 手写找字及其他手写键盘界面不再显示或触发下滑快捷动作\n",
)
replace_once(
    ROOT / "README.md",
    "- 修复数字／符号页面错误显示 QWERTY 下滑功能标签。\n",
    "- 修复数字／符号页面错误显示 QWERTY 下滑功能标签。\n"
    "- 手写找字及其他手写键盘界面不显示标签，也不响应下滑快捷动作。\n",
)
replace_once(
    ROOT / "RELEASE_NOTES_v1.11.3.md",
    "- 修复数字／符号页面错误显示“剪贴、快捷、选前、选后、段首”等 QWERTY 功能标签。\n",
    "- 修复数字／符号页面错误显示“剪贴、快捷、选前、选后、段首”等 QWERTY 功能标签。\n"
    "- 手写找字及其他手写键盘界面不再显示标签或执行下滑动作，避免干扰手写操作。\n",
)

print("Applied handwriting keyboard isolation fix")
