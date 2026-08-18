#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
main_hook = ROOT / "app/src/main/java/com/rww/wetypeswipe/MainHook.java"
text = main_hook.read_text(encoding="utf-8")
old = '''        hook(dispatchTouchEvent)
                .setExceptionMode(XposedInterface.ExceptionMode.PROTECTIVE)
                .intercept(this::interceptDispatchTouch);

        hooksInstalled = true;
'''
new = '''        hook(dispatchTouchEvent)
                .setExceptionMode(XposedInterface.ExceptionMode.PROTECTIVE)
                .intercept(this::interceptDispatchTouch);

        // Settings/About pages can be backed by ViewGroup/Compose containers whose touch
        // dispatch never reaches View.dispatchTouchEvent. Observe ViewGroup separately, but
        // only run the hidden-settings detector here; keyboard gesture handling remains on
        // the existing proven View hook. AboutIconUnlock deduplicates the same ACTION_UP by
        // eventTime, so a physical tap seen by both hooks still counts exactly once.
        Method groupDispatchTouchEvent = ViewGroup.class.getDeclaredMethod(
                "dispatchTouchEvent", MotionEvent.class);
        groupDispatchTouchEvent.setAccessible(true);
        hook(groupDispatchTouchEvent)
                .setExceptionMode(XposedInterface.ExceptionMode.PROTECTIVE)
                .intercept(chain -> {
                    Object groupTarget = chain.getThisObject();
                    Object groupEvent = chain.getArg(0);
                    if (groupTarget instanceof View && groupEvent instanceof MotionEvent) {
                        tryHandleEmbeddedSettingsUnlock((View) groupTarget, (MotionEvent) groupEvent);
                    }
                    return chain.proceed();
                });

        hooksInstalled = true;
'''
if text.count(old) != 1:
    raise SystemExit(f"Expected one View hook block, found {text.count(old)}")
main_hook.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Applied test3 ViewGroup touch fallback")
