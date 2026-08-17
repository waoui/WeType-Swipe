package com.rww.wetypeswipe;

final class AboutIconUnlock {
    static final int REQUIRED_TAPS = 7;
    static final long RESET_GAP_MS = 2_000L;

    private int tapCount;
    private long lastTapAt = Long.MIN_VALUE;

    boolean registerTap(long nowMs) {
        if (lastTapAt == Long.MIN_VALUE || nowMs < lastTapAt || nowMs - lastTapAt > RESET_GAP_MS) {
            tapCount = 0;
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
    }

    int tapCount() {
        return tapCount;
    }
}
