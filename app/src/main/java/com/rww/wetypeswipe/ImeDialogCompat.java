package com.rww.wetypeswipe;

import android.app.AlertDialog;
import android.content.Context;
import android.inputmethodservice.InputMethodService;
import android.os.IBinder;
import android.view.Window;
import android.view.WindowManager;

/** Attaches nested preference dialogs to the input-method window when no Activity exists. */
final class ImeDialogCompat {
    private ImeDialogCompat() {}

    static void show(Context context, AlertDialog dialog) {
        if (context instanceof InputMethodService) {
            IBinder token = inputMethodToken((InputMethodService) context);
            Window window = dialog.getWindow();
            if (window == null || token == null) {
                throw new IllegalStateException("输入法弹窗 Token 不可用");
            }
            window.setType(WindowManager.LayoutParams.TYPE_INPUT_METHOD_DIALOG);
            WindowManager.LayoutParams attributes = window.getAttributes();
            attributes.token = token;
            window.setAttributes(attributes);
        }
        dialog.show();
    }

    static IBinder inputMethodToken(InputMethodService ime) {
        if (ime == null || ime.getWindow() == null || ime.getWindow().getWindow() == null) {
            return null;
        }
        Window window = ime.getWindow().getWindow();
        // The IME window attributes carry the InputMethodService's service token.
        // The decor view's window token identifies the displayed keyboard window,
        // which is NOT interchangeable for TYPE_INPUT_METHOD_DIALOG on some ROMs.
        IBinder serviceToken = window.getAttributes().token;
        return serviceToken != null ? serviceToken : window.getDecorView().getWindowToken();
    }
}
