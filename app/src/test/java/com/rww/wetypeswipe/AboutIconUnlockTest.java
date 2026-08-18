package com.rww.wetypeswipe;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public final class AboutIconUnlockTest {
    private static boolean tap(AboutIconUnlock unlock, long now, long eventTime, float x, float y) {
        return unlock.registerTap(now, eventTime, x, y, 80f);
    }

    @Test public void fifthQuickTapUnlocksAndResets() {
        AboutIconUnlock unlock = new AboutIconUnlock();
        for (int i = 0; i < 4; i++) {
            assertFalse(tap(unlock, 1_000L + i * 200L, 10_000L + i, 500f, 420f));
        }
        assertEquals(4, unlock.tapCount());
        assertTrue(tap(unlock, 1_800L, 10_004L, 500f, 420f));
        assertEquals(0, unlock.tapCount());
    }

    @Test public void duplicateDispatchOfSamePhysicalEventCountsOnce() {
        AboutIconUnlock unlock = new AboutIconUnlock();
        assertFalse(tap(unlock, 1_000L, 100L, 500f, 420f));
        assertFalse(tap(unlock, 1_001L, 100L, 500f, 420f));
        assertFalse(tap(unlock, 1_002L, 100L, 500f, 420f));
        assertEquals(1, unlock.tapCount());
    }

    @Test public void longGapRestartsSequence() {
        AboutIconUnlock unlock = new AboutIconUnlock();
        assertFalse(tap(unlock, 1_000L, 100L, 500f, 420f));
        assertFalse(tap(unlock, 1_200L, 101L, 500f, 420f));
        assertFalse(tap(unlock, 4_000L, 102L, 500f, 420f));
        assertEquals(1, unlock.tapCount());
    }

    @Test public void movingToDifferentAreaRestartsSequence() {
        AboutIconUnlock unlock = new AboutIconUnlock();
        assertFalse(tap(unlock, 1_000L, 100L, 500f, 420f));
        assertFalse(tap(unlock, 1_200L, 101L, 510f, 425f));
        assertFalse(tap(unlock, 1_400L, 102L, 800f, 900f));
        assertEquals(1, unlock.tapCount());
    }

    @Test public void clockRollbackRestartsSequence() {
        AboutIconUnlock unlock = new AboutIconUnlock();
        assertFalse(tap(unlock, 5_000L, 100L, 500f, 420f));
        assertFalse(tap(unlock, 4_000L, 101L, 500f, 420f));
        assertEquals(1, unlock.tapCount());
    }
}
