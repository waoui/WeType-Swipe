#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def rep(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")

# MainHook
p=ROOT / 'app/src/main/java/com/rww/wetypeswipe/MainHook.java'
rep(p,'                config.qwertyLabels[key - \'a\'] = Config.normalizeLabelValue(\n                        intent.getStringExtra(Config.qwertyLabelPrefKey(key)));\n', '                config.qwertyLabels[key - \'a\'] = Config.normalizeLabelValue(\n                        intent.getStringExtra(Config.qwertyLabelPrefKey(key)));\n                config.qwertyTexts[key - \'a\'] = Config.normalizeInsertedText(\n                        intent.getStringExtra(Config.qwertyTextPrefKey(key)));\n')
rep(p,'                config.t9Labels[digit] = Config.normalizeLabelValue(\n                        intent.getStringExtra(Config.t9LabelPrefKey(digit)));\n', '                config.t9Labels[digit] = Config.normalizeLabelValue(\n                        intent.getStringExtra(Config.t9LabelPrefKey(digit)));\n                config.t9Texts[digit] = Config.normalizeInsertedText(\n                        intent.getStringExtra(Config.t9TextPrefKey(digit)));\n')
rep(p,'                editor.putString(Config.qwertyLabelPrefKey(key),\n                        Config.normalizeLabelValue(config.qwertyLabels[key - \'a\']));\n', '                editor.putString(Config.qwertyLabelPrefKey(key),\n                        Config.normalizeLabelValue(config.qwertyLabels[key - \'a\']));\n                editor.putString(Config.qwertyTextPrefKey(key),\n                        Config.normalizeInsertedText(config.qwertyTexts[key - \'a\']));\n')
rep(p,'                editor.putString(Config.t9LabelPrefKey(digit),\n                        Config.normalizeLabelValue(config.t9Labels[digit]));\n', '                editor.putString(Config.t9LabelPrefKey(digit),\n                        Config.normalizeLabelValue(config.t9Labels[digit]));\n                editor.putString(Config.t9TextPrefKey(digit),\n                        Config.normalizeInsertedText(config.t9Texts[digit]));\n')
rep(p,'                config.qwertyLabels[key - \'a\'] = Config.normalizeLabelValue(\n                        prefs.getString(Config.qwertyLabelPrefKey(key), ""));\n', '                config.qwertyLabels[key - \'a\'] = Config.normalizeLabelValue(\n                        prefs.getString(Config.qwertyLabelPrefKey(key), ""));\n                config.qwertyTexts[key - \'a\'] = Config.normalizeInsertedText(\n                        prefs.getString(Config.qwertyTextPrefKey(key), ""));\n')
rep(p,'                config.t9Labels[digit] = Config.normalizeLabelValue(\n                        prefs.getString(Config.t9LabelPrefKey(digit), ""));\n', '                config.t9Labels[digit] = Config.normalizeLabelValue(\n                        prefs.getString(Config.t9LabelPrefKey(digit), ""));\n                config.t9Texts[digit] = Config.normalizeInsertedText(\n                        prefs.getString(Config.t9TextPrefKey(digit), ""));\n')
rep(p,'            boolean success;\n            if (isDocumentAction(action)) {\n', '            boolean success;\n            if (action == Config.ACTION_INSERT_TEXT) {\n                boolean t9 = key != null && key.length() == 1 && key.charAt(0) >= \'2\' && key.charAt(0) <= \'9\';\n                success = performInsertText(connection, cachedConfig.textFor(key, t9));\n            } else if (isDocumentAction(action)) {\n')
rep(p,'\n\n\n\n\n    private static boolean isCompoundAction', '''\n\n    private boolean performInsertText(InputConnection connection, String text) {\n        String value = Config.normalizeInsertedText(text);\n        if (value.isEmpty()) return false;\n        try { connection.finishComposingText(); } catch (Throwable ignored) {}\n        return connection.commitText(value, 1);\n    }\n\n    private static boolean isCompoundAction''')
rep(p,'v1.11.6-test4 entered target package; unified UI five-tap settings enabled','v1.11.6-test5 entered target package; custom text action enabled')
print('Applied test5 runtime custom-text patch')
