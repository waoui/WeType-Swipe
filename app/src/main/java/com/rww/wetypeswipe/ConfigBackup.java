package com.rww.wetypeswipe;

import java.io.IOException;
import java.io.StringReader;
import java.io.StringWriter;
import java.util.HashSet;
import java.util.Properties;
import java.util.Set;

/**
 * Versioned, human-readable UTF-8 key/value backup. Includes only gesture configuration,
 * never credentials, preferences from other applications or Android launcher state.
 */
final class ConfigBackup {
    static final String FORMAT_KEY = "wetype.config.format";
    static final String FORMAT_VERSION = "1";
    static final int MAX_CHARS = 262144;

    private ConfigBackup() {}

    static String exportText(Config source) {
        Properties p = new Properties();
        p.setProperty(FORMAT_KEY, FORMAT_VERSION);
        ConfigCodec.write(new ConfigCodec.Writer() {
            @Override public void putString(String key, String value) {
                p.setProperty(key, value == null ? "" : value);
            }
            @Override public void putInt(String key, int value) {
                p.setProperty(key, String.valueOf(value));
            }
            @Override public void putBoolean(String key, boolean value) {
                p.setProperty(key, String.valueOf(value));
            }
        }, source);
        StringWriter writer = new StringWriter();
        try {
            p.store(writer, "WeType-Swipe UTF-8 gesture configuration; actions 0-24");
        } catch (IOException impossible) {
            throw new IllegalStateException("StringWriter failed", impossible);
        }
        return writer.toString();
    }

    static Config importText(String text) {
        if (text == null || text.trim().isEmpty() || text.length() > MAX_CHARS) {
            throw new IllegalArgumentException("备份为空或超过 256K 字符限制");
        }
        Properties p = new Properties();
        try {
            p.load(new StringReader(text));
        } catch (IOException | IllegalArgumentException ex) {
            throw new IllegalArgumentException("配置内容格式错误", ex);
        }
        if (!FORMAT_VERSION.equals(p.getProperty(FORMAT_KEY))) {
            throw new IllegalArgumentException("不是支持的 WeType-Swipe 配置文件（格式版本 1）");
        }

        // Reject incomplete/corrupt backups instead of silently restoring default values.
        Set<String> required = new HashSet<>();
        ConfigCodec.write(new ConfigCodec.Writer() {
            @Override public void putString(String key, String value) { required.add(key); }
            @Override public void putInt(String key, int value) { required.add(key); }
            @Override public void putBoolean(String key, boolean value) { required.add(key); }
        }, new Config());
        for (String key : required) {
            if (!p.containsKey(key)) {
                throw new IllegalArgumentException("备份缺少字段：" + key);
            }
        }
        for (String key : p.stringPropertyNames()) {
            if (!required.contains(key) && !FORMAT_KEY.equals(key)) {
                throw new IllegalArgumentException("备份含有未知字段：" + key);
            }
        }

        validateBoundedInt(p, Config.KEY_THRESHOLD, 6, 40);
        validateBoundedInt(p, Config.KEY_T9_THRESHOLD, 10, 48);
        validateBoundedInt(p, Config.KEY_REVISION, 0, Integer.MAX_VALUE);
        Config config = ConfigCodec.read(new ConfigCodec.Reader() {
            @Override public String getString(String key, String fallback) {
                return p.getProperty(key, fallback);
            }
            @Override public int getInt(String key, int fallback) {
                try { return Integer.parseInt(p.getProperty(key)); }
                catch (NumberFormatException ex) {
                    throw new IllegalArgumentException("无效整数：" + key, ex);
                }
            }
            @Override public boolean getBoolean(String key, boolean fallback) {
                String value = p.getProperty(key);
                if ("true".equals(value)) return true;
                if ("false".equals(value)) return false;
                throw new IllegalArgumentException("无效布尔值：" + key);
            }
        });

        validate(config, p);
        config.rebuildActionMap();
        return config;
    }

    private static void validate(Config c, Properties p) {
        if (c.thresholdDp < 6 || c.thresholdDp > 40 || c.t9ThresholdDp < 10 || c.t9ThresholdDp > 48) {
            throw new IllegalArgumentException("手势阈值超出合法范围");
        }
        if (c.revision < 0) throw new IllegalArgumentException("版本序号无效");

        boolean[] used = new boolean[26];
        for (int action : ActionRegistry.qwertyActions()) {
            String key = ActionRegistry.keyFor(c, action);
            if (!key.isEmpty()) {
                if (!key.matches("[a-z]")) throw new IllegalArgumentException("无效字母绑定：" + key);
                int i = key.charAt(0) - 'a';
                if (used[i]) throw new IllegalArgumentException("下滑存在重复字母：" + key);
                used[i] = true;
            }
        }
        for (char value : c.disabledKeys.toCharArray()) {
            if (value < 'a' || value > 'z') throw new IllegalArgumentException("无效禁用按键");
            int i = value - 'a';
            if (used[i]) throw new IllegalArgumentException("禁用按键与功能冲突");
            used[i] = true;
        }
        for (char key = 'a'; key <= 'z'; key++) {
            int i = key - 'a';
            String downText = p.getProperty(Config.qwertyTextPrefKey(key));
            String upText = p.getProperty(Config.upQwertyTextPrefKey(key));
            validateText(downText, Config.qwertyTextPrefKey(key));
            validateText(upText, Config.upQwertyTextPrefKey(key));
            validateLabel(p.getProperty(Config.qwertyLabelPrefKey(key)), Config.qwertyLabelPrefKey(key));
            validateLabel(p.getProperty(Config.upQwertyLabelPrefKey(key)), Config.upQwertyLabelPrefKey(key));
            validateAction(p, Config.upQwertyActionPrefKey(key));
            if (!c.qwertyTexts[i].isEmpty() && used[i]) throw new IllegalArgumentException("文字输入与下滑动作冲突");
            if (c.upQwertyActions[i] == Config.ACTION_INSERT_TEXT && c.upQwertyTexts[i].isEmpty()) {
                throw new IllegalArgumentException("上滑自定义输入缺少文字");
            }
        }
        for (int digit = 2; digit <= 9; digit++) {
            validateAction(p, Config.t9PrefKey(digit));
            validateAction(p, Config.upT9ActionPrefKey(digit));
            validateText(p.getProperty(Config.t9TextPrefKey(digit)), Config.t9TextPrefKey(digit));
            validateText(p.getProperty(Config.upT9TextPrefKey(digit)), Config.upT9TextPrefKey(digit));
            validateLabel(p.getProperty(Config.t9LabelPrefKey(digit)), Config.t9LabelPrefKey(digit));
            validateLabel(p.getProperty(Config.upT9LabelPrefKey(digit)), Config.upT9LabelPrefKey(digit));
            if (c.t9Actions[digit] == Config.ACTION_INSERT_TEXT && c.t9Texts[digit].isEmpty()) {
                throw new IllegalArgumentException("九宫格下滑自定义输入缺少文字");
            }
            if (c.upT9Actions[digit] == Config.ACTION_INSERT_TEXT && c.upT9Texts[digit].isEmpty()) {
                throw new IllegalArgumentException("九宫格上滑自定义输入缺少文字");
            }
        }
    }

    private static void validateBoundedInt(Properties p, String key, int min, int max) {
        final int value;
        try { value = Integer.parseInt(p.getProperty(key)); }
        catch (NumberFormatException ex) {
            throw new IllegalArgumentException("无效整数：" + key, ex);
        }
        if (value < min || value > max) {
            throw new IllegalArgumentException("参数超出允许范围：" + key);
        }
    }

    private static void validateAction(Properties p, String key) {
        final int action;
        try { action = Integer.parseInt(p.getProperty(key)); }
        catch (NumberFormatException ex) {
            throw new IllegalArgumentException("无效动作编号：" + key, ex);
        }
        if (Config.validAction(action) != action) {
            throw new IllegalArgumentException("不支持的动作编号：" + key + "=" + action);
        }
    }

    private static void validateText(String text, String key) {
        if (text == null || text.codePointCount(0, text.length()) > 1000
                || text.indexOf('\0') >= 0) {
            throw new IllegalArgumentException("文字内容无效：" + key);
        }
    }

    private static void validateLabel(String label, String key) {
        if (label == null || label.indexOf('\n') >= 0 || label.indexOf('\r') >= 0
                || (!Config.LABEL_HIDDEN.equals(label) && label.codePointCount(0, label.length()) > 4)) {
            throw new IllegalArgumentException("标签内容无效：" + key);
        }
    }
}
