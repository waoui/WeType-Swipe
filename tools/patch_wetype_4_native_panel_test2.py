from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "app/src/main/java/com/rww/wetypeswipe/MainHook.java"
text = path.read_text(encoding="utf-8")

old_field = '''    private volatile Method toolbarCarrierInvokeMethod;\n'''
new_field = '''    private volatile Method toolbarCarrierInvokeMethod;\n    private volatile Method toolbarCarrierDirectInvokeMethod;\n'''
if old_field not in text:
    raise SystemExit("toolbar invoke field not found")
text = text.replace(old_field, new_field, 1)

old_local = '''            Method invokeMethod = toolbarCarrierInvokeMethod;\n\n            if (source == null || !source.isAttachedToWindow()\n'''
new_local = '''            Method invokeMethod = toolbarCarrierInvokeMethod;\n            Method directInvokeMethod = toolbarCarrierDirectInvokeMethod;\n\n            if (source == null || !source.isAttachedToWindow()\n'''
if old_local not in text:
    raise SystemExit("toolbar local invoke block not found")
text = text.replace(old_local, new_local, 1)

old_invoke = '''                View argument = toolbarCarrierArgumentRef.get();\n                if (argument == null) argument = source;\n                invokeMethod.invoke(callback, argument);\n                return true;\n'''
new_invoke = '''                View argument = toolbarCarrierArgumentRef.get();\n                if (argument == null) argument = source;\n                if (directInvokeMethod != null) {\n                    // WeType 4.0.0 wraps the click callback in a Main.immediate coroutine.\n                    // Invoke the concrete ViewHolder click handler directly while the\n                    // temporary function/source/group fields are still active.\n                    directInvokeMethod.invoke(holder, argument);\n                    logInfo("toolbar carrier direct handler invoked holder="\n                            + holder.getClass().getName());\n                } else {\n                    invokeMethod.invoke(callback, argument);\n                }\n                return true;\n'''
if old_invoke not in text:
    raise SystemExit("toolbar callback invocation block not found")
text = text.replace(old_invoke, new_invoke, 1)

old_resolve = '''        Field functionField = findNamedField(holder.getClass(), "f");\n        if (functionField == null) return false;\n        Field categoryField = findNamedField(holder.getClass(), "g");\n        Field groupField = findNamedField(holder.getClass(), "h");\n        Method invokeMethod = findCompatibleInvoke(callback.getClass());\n        if (invokeMethod == null) return false;\n\n        Object permanent = categoryField == null ? null : enumConstant(categoryField.getType(), "Permanent");\n        Object capturedView = readNamedField(callback, "$this_apply");\n        View argument = capturedView instanceof View ? (View) capturedView : source;\n\n        toolbarCarrierRootRef = new WeakReference<>(root);\n        toolbarCarrierSourceRef = new WeakReference<>(source);\n        toolbarCarrierArgumentRef = new WeakReference<>(argument);\n        toolbarCarrierCallback = callback;\n        toolbarCarrierHolder = holder;\n        toolbarCarrierFunctionField = functionField;\n        toolbarCarrierCategoryField = categoryField;\n        toolbarCarrierGroupField = groupField;\n        toolbarCarrierInvokeMethod = invokeMethod;\n        toolbarPermanentCategory = permanent;\n        return true;\n'''
new_resolve = '''        ToolbarCarrierLayout.Fields layout = ToolbarCarrierLayout.resolve(holder.getClass());\n        if (layout == null) return false;\n        Field functionField = layout.function;\n        Field categoryField = layout.category;\n        Field groupField = layout.group;\n        Method invokeMethod = findCompatibleInvoke(callback.getClass());\n        if (invokeMethod == null) return false;\n        Method directInvokeMethod = layout.weType4Layout\n                ? findMethod(holder.getClass(), "g", new Class<?>[]{View.class})\n                : null;\n\n        Object capturedView = readNamedField(callback, "$this_apply");\n        View argument = capturedView instanceof View ? (View) capturedView : source;\n\n        toolbarCarrierRootRef = new WeakReference<>(root);\n        toolbarCarrierSourceRef = new WeakReference<>(source);\n        toolbarCarrierArgumentRef = new WeakReference<>(argument);\n        toolbarCarrierCallback = callback;\n        toolbarCarrierHolder = holder;\n        toolbarCarrierFunctionField = functionField;\n        toolbarCarrierCategoryField = categoryField;\n        toolbarCarrierGroupField = groupField;\n        toolbarCarrierInvokeMethod = invokeMethod;\n        toolbarCarrierDirectInvokeMethod = directInvokeMethod;\n        toolbarPermanentCategory = layout.permanentCategory;\n        logInfo("toolbar carrier layout function=" + functionField.getName()\n                + " category=" + categoryField.getName()\n                + " group=" + groupField.getName()\n                + " direct=" + (directInvokeMethod != null));\n        return true;\n'''
if old_resolve not in text:
    raise SystemExit("toolbar resolve field block not found")
text = text.replace(old_resolve, new_resolve, 1)

old_clear = '''        toolbarCarrierInvokeMethod = null;\n        toolbarPermanentCategory = null;\n'''
new_clear = '''        toolbarCarrierInvokeMethod = null;\n        toolbarCarrierDirectInvokeMethod = null;\n        toolbarPermanentCategory = null;\n'''
if old_clear not in text:
    raise SystemExit("toolbar clear block not found")
text = text.replace(old_clear, new_clear, 1)

old_validate = '''        Field function = findNamedField(holder.getClass(), "f");\n        Field category = findNamedField(holder.getClass(), "g");\n        Field group = findNamedField(holder.getClass(), "h");\n        return function != null && function.getType() == int.class\n                && category != null\n                && group != null && group.getType() == int.class\n                && findCompatibleInvoke(callback.getClass()) != null;\n'''
new_validate = '''        ToolbarCarrierLayout.Fields layout = ToolbarCarrierLayout.resolve(holder.getClass());\n        return layout != null && findCompatibleInvoke(callback.getClass()) != null;\n'''
if old_validate not in text:
    raise SystemExit("toolbar callback validation block not found")
text = text.replace(old_validate, new_validate, 1)

text = text.replace(
    'logInfo("v1.11.7-test1 entered target package; WeType 4.0.0 keyboard compatibility enabled");',
    'logInfo("v1.11.7-test2 entered target package; WeType 4.0.0 keyboard and native-panel compatibility enabled");',
    1,
)

path.write_text(text, encoding="utf-8")

props = root / "gradle.properties"
value = props.read_text(encoding="utf-8")
if "VERSION_CODE=51" not in value or "VERSION_NAME=1.11.7-test1" not in value:
    raise SystemExit("unexpected test1 version")
value = value.replace("VERSION_CODE=51", "VERSION_CODE=52", 1)
value = value.replace("VERSION_NAME=1.11.7-test1", "VERSION_NAME=1.11.7-test2", 1)
props.write_text(value, encoding="utf-8")
