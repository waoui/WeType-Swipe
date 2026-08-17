package com.rww.wetypeswipe;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public final class AboutIconUnlockTest {
    @Test public void seventhQuickTapUnlocksAndResets() {
        AboutIconUnlock unlock = new AboutIconUnlock();
        for (int i = 0; i < 6; i++) {
            assertFalse(unlock.registerTap(1_000L + i * 200L));
        }
        assertEquals(6, unlock.tapCount());
        assertTrue(unlock.registerTap(2_200L));
        assertEquals(0, unlock.tapCount());
    }

    @Test public void longGapRestartsSequence() {
        AboutIconUnlock unlock = new AboutIconUnlock();
        assertFalse(unlock.registerTap(1_000L));
        assertFalse(unlock.registerTap(1_200L));
        assertFalse(unlock.registerTap(4_000L));
        assertEquals(1, unlock.tapCount());
    }

    @Test public void clockRollbackRestartsSequence() {
        AboutIconUnlock unlock = new AboutIconUnlock();
        assertFalse(unlock.registerTap(5_000L));
        assertFalse(unlock.registerTap(4_000L));
        assertEquals(1, unlock.tapCount());
    }
}
