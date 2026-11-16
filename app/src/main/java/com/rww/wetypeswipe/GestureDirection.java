package com.rww.wetypeswipe;

/** Pure direction classifier used by keyboard gestures; screen Y grows downward. */
final class GestureDirection {
    static final int NONE = 0;
    static final int DOWN = 1;
    static final int UP = -1;

    private GestureDirection() {}

    static int resolve(float dx, float dy, float threshold, boolean t9,
                       boolean hasDown, boolean hasUp) {
        float distance = Math.abs(dy);
        if (distance < Math.max(1f, threshold)) return NONE;
        if (!withinHorizontalLimit(dx, distance, threshold, t9)) return NONE;
        if (dy > 0f && hasDown) return DOWN;
        if (dy < 0f && hasUp) return UP;
        return NONE;
    }

    static boolean withinHorizontalLimit(float dx, float distance, float threshold, boolean t9) {
        float limit = t9
                ? Math.max(threshold * 0.9f, distance * 0.75f)
                : Math.max(threshold * 2.5f, distance * 1.2f);
        return Math.abs(dx) <= limit;
    }
}
