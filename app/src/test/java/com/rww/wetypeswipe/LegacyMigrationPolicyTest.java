package com.rww.wetypeswipe;

import static org.junit.Assert.*;
import org.junit.Test;

public final class LegacyMigrationPolicyTest {
    @Test public void importOnlyWhenNoTargetSettingsAndMatchingRequest() {
        assertTrue(LegacyMigrationPolicy.canImport(false, false, "abc", "abc", true));
        assertFalse(LegacyMigrationPolicy.canImport(true, false, "abc", "abc", true));
        assertFalse(LegacyMigrationPolicy.canImport(false, true, "abc", "abc", true));
        assertFalse(LegacyMigrationPolicy.canImport(false, false, null, "abc", true));
        assertFalse(LegacyMigrationPolicy.canImport(false, false, "abc", null, true));
        assertFalse(LegacyMigrationPolicy.canImport(false, false, "abc", "forged", true));
        assertFalse(LegacyMigrationPolicy.canImport(false, false, "abc", "abc", false));
    }

    @Test public void existingWeTypeBindingsAreAuthoritativeRegardlessOfModuleRevision() {
        // A high revision in the old module is not allowed to overwrite the IME cache.
        assertFalse(LegacyMigrationPolicy.canImport(false, true, "same", "same", true));
    }
}
