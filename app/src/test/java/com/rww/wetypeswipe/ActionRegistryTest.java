package com.rww.wetypeswipe;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public final class ActionRegistryTest {
    @Test public void everyPublishedActionIdIsRegisteredExactlyOnce() {
        int[] expected = new int[24];
        for (int i = 0; i < expected.length; i++) expected[i] = i;
        assertArrayEquals(expected, ActionRegistry.registeredIds());
        assertEquals(24, ActionRegistry.registeredCount());
    }

    @Test public void menuRoundTripsEveryPosition() {
        assertEquals(ActionRegistry.menuCount(), Config.ACTION_MENU_LABELS.length);
        for (int position = 0; position < ActionRegistry.menuCount(); position++) {
            int action = Config.actionForMenuPosition(position);
            assertEquals(position, Config.menuPositionForAction(action));
            assertEquals(ActionRegistry.name(action), Config.ACTION_MENU_LABELS[position]);
        }
    }

    @Test public void qwertyRegistryOwnsStorageAndMetadata() {
        Config config = new Config();
        int index = 0;
        for (int action : ActionRegistry.qwertyActions()) {
            String key = String.valueOf((char) ('a' + index++));
            assertTrue(ActionRegistry.qwertyContains(action));
            assertFalse(ActionRegistry.storageKey(action).isEmpty());
            ActionRegistry.setKey(config, action, key);
            assertEquals(key, ActionRegistry.keyFor(config, action));
            assertFalse(ActionRegistry.name(action).isEmpty());
        }
    }

    @Test public void systemInputMethodActionsKeepPasswordSemantics() {
        assertTrue(ActionRegistry.isInputMethodAction(Config.ACTION_NEXT_INPUT_METHOD));
        assertTrue(ActionRegistry.isInputMethodAction(Config.ACTION_PREVIOUS_INPUT_METHOD));
        assertTrue(ActionRegistry.isInputMethodAction(Config.ACTION_SHOW_INPUT_METHOD_PICKER));
        assertTrue(ActionRegistry.allowsInPassword(Config.ACTION_NEXT_INPUT_METHOD));
        assertFalse(ActionRegistry.allowsInPassword(Config.ACTION_COPY));
    }
}
