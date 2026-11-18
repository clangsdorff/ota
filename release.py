#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: 2026 Langsdorff
# SPDX-License-Identifier: Apache-2.0
#

import argparse
import glob
import hashlib
import json
import os
import re
import zipfile

REPO = "clangsdorff/ota"
ROOT = os.path.dirname(os.path.abspath(__file__))
WIKI = "https://github.com/clangsdorff/android_device_samsung_a14/wiki"
DEVICES = {
    "a14": ("Galaxy A14 4G (SM-A145F)", "SM-A145F", "a13", "Installation-A14"),
    "a13": ("Galaxy A13 (SM-A135F)", "SM-A135F", "a14", "Installation-A13"),
}


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


def entry(path, tag, version, rtype, m=None):
    if m is None:
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
    p.add_argument("--recovery", help="lineage-<device>-recovery.tar.md5 for odin")
    a = p.parse_args()

    name = os.path.basename(a.full)
    r = re.match(r"lineage-([\d.]+)-\d+-(\w+)-(\w+)\.zip$", name)
    if not r:
        raise SystemExit(f"unexpected file name: {name}")
    version, rtype, device = r.groups()

    m = metadata(a.full)
    incr = m["post-build-incremental"]
    tag = f"{device}-{incr}"

    full = entry(a.full, tag, version, rtype, m)
    with open(os.path.join(ROOT, f"{device}.json"), "w") as f:
        json.dump([full], f, indent=2)
        f.write("\n")

    ddir = os.path.join(ROOT, device)
    if os.path.isdir(ddir):
        for old in glob.glob(os.path.join(ddir, "*.json")):
            os.remove(old)

    if a.incremental:
        im = metadata(a.incremental)
        if im.get("post-build-incremental") != incr:
            raise SystemExit("incremental target does not match the full ota")
        pre_incr = im.get("pre-build-incremental")
        if not pre_incr:
            raise SystemExit("incremental zip missing pre-build-incremental")
        os.makedirs(ddir, exist_ok=True)
        inc = entry(a.incremental, tag, version, rtype, im)
        with open(os.path.join(ddir, f"{pre_incr}.json"), "w") as f:
            json.dump([inc], f, indent=2)
            f.write("\n")

    name, model, other, page = DEVICES[device]
    notes = (f"**Only for {model}. Do not flash on any other phone, "
             f"{other} files are in the {other}- releases.**\n\n"
             f"Installation: {WIKI}/{page}\n"
             f"Updating: {WIKI}/Updating")
    assets = [a.full] + [x for x in (a.incremental, a.recovery) if x]
    print(f"gh release create {tag} " + " ".join(assets)
          + f" -R {REPO} -t '{name} {version} {m['post-build-incremental']}' --latest=false"
          + f" -n {json.dumps(notes)}")


if __name__ == "__main__":
    main()
