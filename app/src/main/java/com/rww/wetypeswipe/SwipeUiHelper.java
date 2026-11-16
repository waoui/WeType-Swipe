package com.rww.wetypeswipe;

import android.content.Context;
import android.app.AlertDialog;

/** Shared affordances for embedded and standalone settings. */
final class SwipeUiHelper {
    interface DirectionChoice { void selected(boolean upward); }

    private SwipeUiHelper() {}

    static void chooseDirection(Context activity, String key, String purpose,
                                DirectionChoice callback) {
        AlertDialog dialog = new AlertDialog.Builder(activity)
                .setTitle(key + " · " + purpose)
                .setItems(new String[]{"↓ 下滑", "↑ 上滑"}, (selectedDialog, selected) -> {
                    if (callback != null) callback.selected(selected == 1);
                })
                .setNegativeButton("取消", null)
                .create();
        ImeDialogCompat.show(activity, dialog);
    }

    static String[] actionMenu(boolean upward) {
        String[] labels = Config.ACTION_MENU_LABELS.clone();
        labels[Config.menuPositionForAction(Config.ACTION_DISABLE)] =
                upward ? "禁用上滑" : "禁用下滑";
        return labels;
    }

    static String directionalPreview(String down, String up) {
        return "↓" + (down == null ? "—" : down) + "\n↑" + (up == null ? "—" : up);
    }
}
