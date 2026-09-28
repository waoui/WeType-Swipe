package com.rww.wetypeswipe;

import android.view.View;

/** WeType keyboard compatibility identification kept outside the hook orchestration. */
final class KeyboardCompat {
    private static final String LEGACY_KEYBOARD_BASE =
            "com.tencent.wetype.plugin.hld.keyboard.selfdraw.n";
    private static final String WETYPE_4_KEYBOARD_BASE =
            "com.tencent.wetype.plugin.hld.keyboard.selfdraw.o";
    private static final String SELF_DRAW_PREFIX =
            "com.tencent.wetype.plugin.hld.keyboard.selfdraw.";

    private KeyboardCompat() {}

    static Class<?> findKeyboardBase(Class<?> type) {
        for (int i = 0; type != null && i < 12; i++, type = type.getSuperclass()) {
            String name = type.getName();
            if (LEGACY_KEYBOARD_BASE.equals(name) || WETYPE_4_KEYBOARD_BASE.equals(name)) {
                return type;
            }
            if (name.startsWith(SELF_DRAW_PREFIX)
                    && View.class.isAssignableFrom(type)
                    && declaresNoArg(type, "getActionButton")
                    && declaresNoArg(type, "getKeysLayoutInfo")) {
                return type;
            }
        }
        return null;
    }

    static boolean isHandwritingContext(View keyboard) {
        View current = keyboard;
        for (int depth = 0; current != null && depth < 16; depth++) {
            if (KeyboardModeGuard.isHandwritingClassName(current.getClass().getName())) return true;
            Object parent = current.getParent();
            current = parent instanceof View ? (View) parent : null;
        }
        return false;
    }

    private static boolean declaresNoArg(Class<?> type, String name) {
        if (type == null || name == null) return false;
        try {
            type.getDeclaredMethod(name);
            return true;
        } catch (NoSuchMethodException ignored) {
            return false;
        } catch (Throwable ignored) {
            return false;
        }
    }
}
