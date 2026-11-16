package com.rww.wetypeswipe;

import static org.junit.Assert.assertEquals;
import org.junit.Test;

public final class ConfigRevisionPolicyTest {
    @Test public void automaticSyncAcceptsEqualOrNewerRevisions() {
        assertEquals(12, ConfigRevisionPolicy.revisionForSnapshot(12, 12, false));
        assertEquals(14, ConfigRevisionPolicy.revisionForSnapshot(14, 12, false));
        assertEquals(0, ConfigRevisionPolicy.revisionForSnapshot(0, -1, false));
    }

    @Test public void automaticSyncNeverSilentlyRollsBackLatestModuleChanges() {
        assertEquals(-1, ConfigRevisionPolicy.revisionForSnapshot(5, 18, false));
        assertEquals(-1, ConfigRevisionPolicy.revisionForSnapshot(-1, 18, false));
    }

    @Test public void confirmedManualRecoveryKeepsRevisionMonotonic() {
        assertEquals(19, ConfigRevisionPolicy.revisionForSnapshot(5, 18, true));
        assertEquals(19, ConfigRevisionPolicy.revisionForSnapshot(19, 18, true));
        assertEquals(-1, ConfigRevisionPolicy.revisionForSnapshot(0, Integer.MAX_VALUE, true));
    }
}
