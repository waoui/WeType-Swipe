package com.rww.wetypeswipe;

import android.content.Intent;

final class ConfigSnapshot {
    private ConfigSnapshot() {}

    static Config copyOf(Config source) {
        Config target = new Config();
        if (source == null) {
            target.rebuildActionMap();
            return target;
        }
        target.selectAll = source.selectAll;
        target.cut = source.cut;
        target.copy = source.copy;
        target.paste = source.paste;
        target.copyAll = source.copyAll;
        target.cutAll = source.cutAll;
        target.paragraphStart = source.paragraphStart;
        target.paragraphEnd = source.paragraphEnd;
        target.selectToParagraphStart = source.selectToParagraphStart;
        target.selectToParagraphEnd = source.selectToParagraphEnd;
        target.documentStart = source.documentStart;
        target.documentEnd = source.documentEnd;
        target.selectToDocumentStart = source.selectToDocumentStart;
        target.selectToDocumentEnd = source.selectToDocumentEnd;
        target.openClipboard = source.openClipboard;
        target.openQuickPhrase = source.openQuickPhrase;
        target.undo = source.undo;
        target.redo = source.redo;
        target.disabledKeys = source.disabledKeys;
        target.thresholdDp = source.thresholdDp;
        target.t9ThresholdDp = source.t9ThresholdDp;
        target.vibration = source.vibration;
        target.showKeyLabels = source.showKeyLabels;
        target.showTriggerHint = source.showTriggerHint;
        target.revision = source.revision;
        System.arraycopy(source.t9Actions, 0, target.t9Actions, 0, source.t9Actions.length);
        System.arraycopy(source.qwertyLabels, 0, target.qwertyLabels, 0, source.qwertyLabels.length);
        System.arraycopy(source.t9Labels, 0, target.t9Labels, 0, source.t9Labels.length);
        target.rebuildActionMap();
        return target;
    }

    static void putInto(Intent intent, Config config) {
        intent.putExtra(Config.EXTRA_SNAPSHOT, true);
        intent.putExtra(Config.KEY_SELECT_ALL, config.selectAll);
        intent.putExtra(Config.KEY_CUT, config.cut);
        intent.putExtra(Config.KEY_COPY, config.copy);
        intent.putExtra(Config.KEY_PASTE, config.paste);
        intent.putExtra(Config.KEY_COPY_ALL, config.copyAll);
        intent.putExtra(Config.KEY_CUT_ALL, config.cutAll);
        intent.putExtra(Config.KEY_PARAGRAPH_START, config.paragraphStart);
        intent.putExtra(Config.KEY_PARAGRAPH_END, config.paragraphEnd);
        intent.putExtra(Config.KEY_SELECT_TO_PARAGRAPH_START, config.selectToParagraphStart);
        intent.putExtra(Config.KEY_SELECT_TO_PARAGRAPH_END, config.selectToParagraphEnd);
        intent.putExtra(Config.KEY_DOCUMENT_START, config.documentStart);
        intent.putExtra(Config.KEY_DOCUMENT_END, config.documentEnd);
        intent.putExtra(Config.KEY_SELECT_TO_DOCUMENT_START, config.selectToDocumentStart);
        intent.putExtra(Config.KEY_SELECT_TO_DOCUMENT_END, config.selectToDocumentEnd);
        intent.putExtra(Config.KEY_OPEN_CLIPBOARD, config.openClipboard);
        intent.putExtra(Config.KEY_OPEN_QUICK_PHRASE, config.openQuickPhrase);
        intent.putExtra(Config.KEY_UNDO, config.undo);
        intent.putExtra(Config.KEY_REDO, config.redo);
        intent.putExtra(Config.KEY_DISABLED_KEYS, config.disabledKeys);
        intent.putExtra(Config.KEY_THRESHOLD, config.thresholdDp);
        intent.putExtra(Config.KEY_T9_THRESHOLD, config.t9ThresholdDp);
        intent.putExtra(Config.KEY_VIBRATION, config.vibration);
        intent.putExtra(Config.KEY_SHOW_KEY_LABELS, config.showKeyLabels);
        intent.putExtra(Config.KEY_SHOW_TRIGGER_HINT, config.showTriggerHint);
        intent.putExtra(Config.KEY_REVISION, config.revision);
        for (char key = 'a'; key <= 'z'; key++) {
            intent.putExtra(Config.qwertyLabelPrefKey(key),
                    Config.normalizeLabelValue(config.qwertyLabels[key - 'a']));
        }
        for (int digit = 2; digit <= 9; digit++) {
            intent.putExtra(Config.t9PrefKey(digit), config.t9Actions[digit]);
            intent.putExtra(Config.t9LabelPrefKey(digit),
                    Config.normalizeLabelValue(config.t9Labels[digit]));
        }
    }
}
