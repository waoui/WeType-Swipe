package com.rww.wetypeswipe;

/** Precomputed immutable labels for the keyboard drawing hot path. */
final class KeyboardLabelSnapshot {
    private static final KeyboardLabelSnapshot EMPTY =
            new KeyboardLabelSnapshot(new String[26], new String[10], false);

    private final String[] qwertyLabels;
    private final String[] t9Labels;
    private final boolean hasAnyLabels;

    private KeyboardLabelSnapshot(String[] qwertyLabels, String[] t9Labels,
                                  boolean hasAnyLabels) {
        this.qwertyLabels = qwertyLabels;
        this.t9Labels = t9Labels;
        this.hasAnyLabels = hasAnyLabels;
    }

    static KeyboardLabelSnapshot empty() {
        return EMPTY;
    }

    static KeyboardLabelSnapshot from(Config config) {
        if (config == null || !config.showKeyLabels || !config.hasAnyBinding()) return EMPTY;

        String[] qwerty = new String[26];
        String[] t9 = new String[10];
        boolean any = false;

        for (int index = 0; index < 26; index++) {
            String key = String.valueOf((char) ('a' + index));
            int action = config.actionFor(key, false);
            if (action == Config.ACTION_NONE || action == Config.ACTION_DISABLE) continue;
            String label = config.labelFor(key, false, action);
            if (label == null || label.isEmpty()) continue;
            qwerty[index] = label;
            any = true;
        }

        for (int digit = 2; digit <= 9; digit++) {
            String key = String.valueOf((char) ('0' + digit));
            int action = config.actionFor(key, true);
            if (action == Config.ACTION_NONE || action == Config.ACTION_DISABLE) continue;
            String label = config.labelFor(key, true, action);
            if (label == null || label.isEmpty()) continue;
            t9[digit] = label;
            any = true;
        }

        return any ? new KeyboardLabelSnapshot(qwerty, t9, true) : EMPTY;
    }

    boolean hasAnyLabels() {
        return hasAnyLabels;
    }

    String labelFor(String key, boolean t9) {
        if (!hasAnyLabels || key == null || key.length() != 1) return "";
        char value = Character.toLowerCase(key.charAt(0));
        String label;
        if (t9) {
            if (value < '2' || value > '9') return "";
            label = t9Labels[value - '0'];
        } else {
            if (value < 'a' || value > 'z') return "";
            label = qwertyLabels[value - 'a'];
        }
        return label == null ? "" : label;
    }
}
