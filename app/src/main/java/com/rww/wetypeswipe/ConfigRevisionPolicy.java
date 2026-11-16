package com.rww.wetypeswipe;

/** Deterministic policy for resolving divergent local and active-IME revisions. */
final class ConfigRevisionPolicy {
    private ConfigRevisionPolicy() {}

    /**
     * @return revision to persist; -1 means reject automatic older snapshot.
     */
    static int revisionForSnapshot(int incoming, int stored, boolean manual) {
        if (incoming < 0) return -1;
        if (incoming >= stored) return incoming;
        if (!manual) return -1;
        if (stored == Integer.MAX_VALUE) return -1;
        return stored + 1;
    }
}
