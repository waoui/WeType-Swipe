from pathlib import Path
import runpy
import subprocess

base_test7_commit = "343d43e2a5081c635e4def3716995b69793ca07d"
base_test8_commit = "d7e2367f518a5bfc01d77e056a319d0a1e42466c"

subprocess.run(["git", "fetch", "origin", base_test7_commit, base_test8_commit], check=True)

with open("tools/patch_v111_test7.py", "wb") as output:
    subprocess.run([
        "git", "show", base_test7_commit + ":tools/patch_v111_test7.py"
    ], check=True, stdout=output)

base_path = Path("/tmp/patch_v111_test8_base.py")
with base_path.open("wb") as output:
    subprocess.run([
        "git", "show", base_test8_commit + ":tools/patch_v111_test8_fix.py"
    ], check=True, stdout=output)

runpy.run_path(str(base_path), run_name="__main__")
runpy.run_path("tools/patch_v111_test9_after.py", run_name="__main__")

print("v1.11.0-test9 pinned edge-key geometry build applied")
