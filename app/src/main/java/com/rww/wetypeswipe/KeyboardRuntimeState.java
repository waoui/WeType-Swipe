package com.rww.wetypeswipe;

import android.view.View;

/** Immutable per-active-keyboard classification used by touch and draw hot paths. */
final class KeyboardRuntimeState {
    enum Mode { QWERTY, T9, HANDWRITING, OTHER }

    final Mode mode;
    final boolean handwriting;

    private KeyboardRuntimeState(Mode mode, boolean handwriting) {
        this.mode = mode;
        this.handwriting = handwriting;
    }

    static KeyboardRuntimeState from(View keyboard) {
        if (keyboard == null) return new KeyboardRuntimeState(Mode.OTHER, false);
        boolean handwriting = KeyboardCompat.isHandwritingContext(keyboard);
        return classify(keyboard.getClass().getName(), handwriting);
    }

    static KeyboardRuntimeState classify(String className, boolean handwriting) {
        if (handwriting) return new KeyboardRuntimeState(Mode.HANDWRITING, true);
        String name = className == null ? "" : className.toLowerCase(java.util.Locale.ROOT);
        if (name.contains("t9") || name.contains("nine")) {
            return new KeyboardRuntimeState(Mode.T9, false);
        }
        if (name.contains("qwerty") || name.contains("wubi") || name.contains("pinyin")) {
            return new KeyboardRuntimeState(Mode.QWERTY, false);
        }
        return new KeyboardRuntimeState(Mode.OTHER, false);
    }
}
