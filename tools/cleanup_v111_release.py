from pathlib import Path

for path in Path("tools").glob("patch_v111_*.py"):
    path.unlink(missing_ok=True)

for path in Path(".github/workflows").glob("test-v1.11.0-*.yml"):
    path.unlink(missing_ok=True)

Path(".release-prepare-v1.11.0").unlink(missing_ok=True)
Path(".github/workflows/prepare-v1.11.0-release.yml").unlink(missing_ok=True)
Path("tools/prepare_v111_release.py").unlink(missing_ok=True)
Path("tools/cleanup_v111_release.py").unlink(missing_ok=True)

print("v1.11.0 test assets removed")
