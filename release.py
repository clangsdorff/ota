#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: 2026 Langsdorff
# SPDX-License-Identifier: Apache-2.0
#

import argparse
import hashlib
import json
import os
import re
import zipfile

REPO = "clangsdorff/ota"
ROOT = os.path.dirname(os.path.abspath(__file__))


def metadata(path):
    with zipfile.ZipFile(path) as z:
        text = z.read("META-INF/com/android/metadata").decode()
    return dict(l.split("=", 1) for l in text.splitlines() if "=" in l)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("full", help="full ota zip")
    a = p.parse_args()

    name = os.path.basename(a.full)
    r = re.match(r"lineage-([\d.]+)-\d+-(\w+)-(\w+)\.zip$", name)
    if not r:
        raise SystemExit(f"unexpected file name: {name}")
    version, rtype, device = r.groups()

    m = metadata(a.full)
    tag = f"{device}-{m['post-build-incremental']}"
    update = {
        "datetime": int(m["post-timestamp"]),
        "type": rtype,
        "version": version,
        "files": [{
            "filename": name,
            "os_patch_level": m.get("post-security-patch-level"),
            "os_sdk_level": int(m["post-sdk-level"]),
            "sha256": sha256(a.full),
            "size": os.path.getsize(a.full),
            "url": f"https://github.com/{REPO}/releases/download/{tag}/{name}",
        }],
    }

    with open(os.path.join(ROOT, f"{device}.json"), "w") as f:
        json.dump([update], f, indent=2)
        f.write("\n")

    print(f"gh release create {tag} {a.full} -R {REPO} -t {tag} -n ''")


if __name__ == "__main__":
    main()
