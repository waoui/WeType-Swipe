package com.rww.wetypeswipe;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public class KeyboardLabelSnapshotTest {
    @Test public void defaultQwertyLabelsArePrecomputed() {
        Config config = new Config();
        config.rebuildActionMap();

        KeyboardLabelSnapshot snapshot = KeyboardLabelSnapshot.from(config);

        assertTrue(snapshot.hasAnyLabels());
        assertEquals("全选", snapshot.labelFor("z", false));
        assertEquals("剪切", snapshot.labelFor("x", false));
        assertEquals("复制", snapshot.labelFor("c", false));
        assertEquals("粘贴", snapshot.labelFor("v", false));
        assertEquals("", snapshot.labelFor("a", false));
    }

    @Test public void hiddenAndDisabledLabelsStayHidden() {
        Config config = new Config();
        config.qwertyLabels['z' - 'a'] = Config.LABEL_HIDDEN;
        config.rebuildActionMap();

        KeyboardLabelSnapshot snapshot = KeyboardLabelSnapshot.from(config);
        assertEquals("", snapshot.labelFor("z", false));

        config.showKeyLabels = false;
        snapshot = KeyboardLabelSnapshot.from(config);
        assertFalse(snapshot.hasAnyLabels());
    }

    @Test public void t9LabelsUseTheSamePublishedActionNames() {
        Config config = new Config();
        config.t9Actions[2] = Config.ACTION_COPY;
        config.rebuildActionMap();

        KeyboardLabelSnapshot snapshot = KeyboardLabelSnapshot.from(config);
        assertEquals("复制", snapshot.labelFor("2", true));
    }
}
