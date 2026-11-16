package com.rww.wetypeswipe;

/**
 * Pure gate for a one-time move of old standalone preferences into WeType.
 * An already-present WeType cache is never replaced by historical module data.
 */
final class LegacyMigrationPolicy {
    private LegacyMigrationPolicy() {}

    static boolean canImport(boolean targetLoaded, boolean targetHasSavedRevision,
                             String expectedToken, String responseToken, boolean hasSnapshot) {
        return !targetLoaded && !targetHasSavedRevision && hasSnapshot
                && expectedToken != null && !expectedToken.isEmpty()
                && expectedToken.equals(responseToken);
    }
}
