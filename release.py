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


def entry(path, tag, version, rtype):
    m = metadata(path)
    name = os.path.basename(path)
    return {
        "datetime": int(m["post-timestamp"]),
        "type": rtype,
        "version": version,
        "files": [{
            "filename": name,
            "os_patch_level": m.get("post-security-patch-level"),
            "os_sdk_level": int(m["post-sdk-level"]),
            "sha256": sha256(path),
            "size": os.path.getsize(path),
            "url": f"https://github.com/{REPO}/releases/download/{tag}/{name}",
        }],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("full", help="full ota zip")
    p.add_argument("--incremental", help="incremental ota zip from the previous build")
    a = p.parse_args()

    name = os.path.basename(a.full)
    r = re.match(r"lineage-([\d.]+)-\d+-(\w+)-(\w+)\.zip$", name)
    if not r:
        raise SystemExit(f"unexpected file name: {name}")
    version, rtype, device = r.groups()

    m = metadata(a.full)
    incr = m["post-build-incremental"]
    tag = f"{device}-{incr}"

    ddir = os.path.join(ROOT, device)
    os.makedirs(ddir, exist_ok=True)
    state_path = os.path.join(ddir, "builds.json")
    builds = json.load(open(state_path)) if os.path.exists(state_path) else []
    if incr in builds:
        raise SystemExit(f"{incr} already released")

    full = entry(a.full, tag, version, rtype)
    inc_base = None
    inc = None
    if a.incremental:
        im = metadata(a.incremental)
        if im.get("post-build-incremental") != incr:
            raise SystemExit("incremental target does not match the full ota")
        inc_base = im["pre-build-incremental"]
        if inc_base not in builds:
            raise SystemExit(f"incremental base {inc_base} was never released")
        inc = entry(a.incremental, tag, version, rtype)

    builds.append(incr)
    for b in builds:
        out = [] if b == incr else [inc if b == inc_base else full]
        with open(os.path.join(ddir, f"{b}.json"), "w") as f:
            json.dump(out, f, indent=2)
            f.write("\n")
    with open(state_path, "w") as f:
        json.dump(builds, f, indent=2)
        f.write("\n")

    assets = [a.full] + ([a.incremental] if a.incremental else [])
    print(f"tag: {tag}")
    print("gh release create " + tag + " " + " ".join(assets) + f" -R {REPO} -t {tag} -n ''")


if __name__ == "__main__":
    main()
