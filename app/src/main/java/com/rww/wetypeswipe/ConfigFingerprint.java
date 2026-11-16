package com.rww.wetypeswipe;

/** Stable, type-aware fingerprint of editable settings, excluding sync revision metadata. */
final class ConfigFingerprint {
    private ConfigFingerprint() {}

    static String of(Config config) {
        StringBuilder builder = new StringBuilder(4096);
        ConfigCodec.write(new ConfigCodec.Writer() {
            private void append(String key, String type, String value) {
                if (Config.KEY_REVISION.equals(key)) return;
                builder.append(key.length()).append(':').append(key)
                        .append(type).append(value.length()).append(':').append(value);
            }
            @Override public void putString(String key, String value) {
                append(key, "S", value == null ? "" : value);
            }
            @Override public void putInt(String key, int value) {
                append(key, "I", Integer.toString(value));
            }
            @Override public void putBoolean(String key, boolean value) {
                append(key, "B", Boolean.toString(value));
            }
        }, config);
        return builder.toString();
    }
}
