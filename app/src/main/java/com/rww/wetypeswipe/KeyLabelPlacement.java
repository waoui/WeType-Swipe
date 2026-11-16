package com.rww.wetypeswipe;

/** Baselines for separate labels at the upper and lower edges of a key. */
final class KeyLabelPlacement {
    private KeyLabelPlacement() {}

    static float upBaseline(float keyTop, float padding, float fontAscent) {
        return keyTop + padding - fontAscent;
    }

    static float downBaseline(float keyBottom, float padding, float fontDescent) {
        return keyBottom - padding - fontDescent;
    }
}
