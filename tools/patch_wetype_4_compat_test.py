from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "app/src/main/java/com/rww/wetypeswipe/MainHook.java"
text = path.read_text(encoding="utf-8")

old_const = '''    private static final String KEYBOARD_BASE = "com.tencent.wetype.plugin.hld.keyboard.selfdraw.n";\n'''
new_const = '''    private static final String LEGACY_KEYBOARD_BASE = "com.tencent.wetype.plugin.hld.keyboard.selfdraw.n";\n    private static final String WETYPE_4_KEYBOARD_BASE = "com.tencent.wetype.plugin.hld.keyboard.selfdraw.o";\n    private static final String SELF_DRAW_PREFIX = "com.tencent.wetype.plugin.hld.keyboard.selfdraw.";\n'''
if old_const not in text:
    raise SystemExit("legacy keyboard base constant not found")
text = text.replace(old_const, new_const, 1)

old_find = '''    private static Class<?> findKeyboardBase(Class<?> type) {\n        for (int i = 0; type != null && i < 12; i++, type = type.getSuperclass()) {\n            if (KEYBOARD_BASE.equals(type.getName())) return type;\n        }\n        return null;\n    }\n'''
new_find = '''    private static Class<?> findKeyboardBase(Class<?> type) {\n        for (int i = 0; type != null && i < 12; i++, type = type.getSuperclass()) {\n            String name = type.getName();\n            if (LEGACY_KEYBOARD_BASE.equals(name) || WETYPE_4_KEYBOARD_BASE.equals(name)) {\n                return type;\n            }\n            // WeType 4.0.0 changed the obfuscated self-draw base from `n` to `o`.\n            // Keep a structural fallback so future one-letter renames do not disable the\n            // whole module again. Only accept a selfdraw View class that declares both\n            // stable keyboard accessors on that exact class (not inherited by a concrete\n            // QWERTY/T9 subclass), otherwise caching one layout would exclude the others.\n            if (name.startsWith(SELF_DRAW_PREFIX)\n                    && View.class.isAssignableFrom(type)\n                    && declaresNoArg(type, "getActionButton")\n                    && declaresNoArg(type, "getKeysLayoutInfo")) {\n                return type;\n            }\n        }\n        return null;\n    }\n\n    private static boolean declaresNoArg(Class<?> type, String name) {\n        if (type == null || name == null) return false;\n        try {\n            type.getDeclaredMethod(name);\n            return true;\n        } catch (NoSuchMethodException ignored) {\n            return false;\n        } catch (Throwable ignored) {\n            return false;\n        }\n    }\n'''
if old_find not in text:
    raise SystemExit("findKeyboardBase block not found")
text = text.replace(old_find, new_find, 1)

text = text.replace(
    'logInfo("v1.11.6 entered target package; embedded settings and custom text enabled");',
    'logInfo("v1.11.7-test1 entered target package; WeType 4.0.0 keyboard compatibility enabled");',
    1,
)

path.write_text(text, encoding="utf-8")

props = root / "gradle.properties"
value = props.read_text(encoding="utf-8")
if "VERSION_CODE=50" not in value or "VERSION_NAME=1.11.6" not in value:
    raise SystemExit("unexpected base version")
value = value.replace("VERSION_CODE=50", "VERSION_CODE=51", 1)
value = value.replace("VERSION_NAME=1.11.6", "VERSION_NAME=1.11.7-test1", 1)
props.write_text(value, encoding="utf-8")
