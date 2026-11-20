"""Download the SkillCorner open data (A-League 2024/25, 20 matches) into data/matches/.

Usage: python scripts/download_data.py
Needs git. About 1.9 GB. The data is not stored in this repository.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

REPO = "https://github.com/SkillCorner/opendata"
MEDIA = "https://media.githubusercontent.com/media/SkillCorner/opendata/master/"
DEST = Path(__file__).resolve().parents[1] / "data" / "matches"


def main():
    if DEST.exists() and any(DEST.iterdir()):
        print(f"{DEST} already has data; delete it to re-download.")
        return
    with tempfile.TemporaryDirectory() as tmp:
        # Clone without the large tracking files (they are stored with Git LFS).
        env = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1")
        subprocess.run(["git", "clone", "--depth", "1", REPO, tmp], check=True, env=env)
        shutil.copytree(Path(tmp) / "data" / "matches", DEST)

    # Replace each LFS pointer with the real tracking file, checking its hash.
    for pointer in sorted(DEST.glob("*/*_tracking_extrapolated.jsonl")):
        text = pointer.read_text()[:200]
        if not text.startswith("version https://git-lfs"):
            continue
        oid = text.split("oid sha256:")[1].split()[0]
        rel = pointer.relative_to(DEST.parent.parent).as_posix()
        print(f"downloading {pointer.name} ...", flush=True)
        tmpfile = pointer.with_suffix(".part")
        urllib.request.urlretrieve(MEDIA + rel, tmpfile)
        if hashlib.sha256(tmpfile.read_bytes()).hexdigest() != oid:
            sys.exit(f"checksum mismatch for {pointer.name}")
        tmpfile.replace(pointer)
    print(f"done: {DEST}")


if __name__ == "__main__":
    main()
