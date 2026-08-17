package com.rww.wetypeswipe;

final class AboutIconUnlock {
    static final int REQUIRED_TAPS = 7;
    static final long RESET_GAP_MS = 2_000L;

    private int tapCount;
    private long lastTapAt = Long.MIN_VALUE;
    private long lastEventTime = Long.MIN_VALUE;
    private float anchorX;
    private float anchorY;
    private boolean hasAnchor;

    boolean registerTap(long nowMs, long eventTimeMs, float x, float y, float tolerancePx) {
        if (eventTimeMs == lastEventTime) return false;
        lastEventTime = eventTimeMs;

        boolean timeout = lastTapAt != Long.MIN_VALUE
                && (nowMs < lastTapAt || nowMs - lastTapAt > RESET_GAP_MS);
        boolean moved = hasAnchor && distanceSquared(anchorX, anchorY, x, y)
                > tolerancePx * tolerancePx;
        if (timeout || moved) {
            tapCount = 0;
            hasAnchor = false;
        }

        if (!hasAnchor) {
            anchorX = x;
            anchorY = y;
            hasAnchor = true;
        }
        lastTapAt = nowMs;
        tapCount++;
        if (tapCount >= REQUIRED_TAPS) {
            reset();
            return true;
        }
        return false;
    }

    void reset() {
        tapCount = 0;
        lastTapAt = Long.MIN_VALUE;
        lastEventTime = Long.MIN_VALUE;
        hasAnchor = false;
        anchorX = 0f;
        anchorY = 0f;
    }

    int tapCount() {
        return tapCount;
    }

    private static float distanceSquared(float x1, float y1, float x2, float y2) {
        float dx = x1 - x2;
        float dy = y1 - y2;
        return dx * dx + dy * dy;
    }
}
