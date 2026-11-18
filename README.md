# ota

Updater feed for langsdorff builds. Devices fetch `<device>/<incremental>.json` and fall back to `<device>.json` for full updates.

Publishing a release with `lineage-*.zip` assets updates the feed through the `feed` workflow. Releases tagged `target-files-*` are ignored by the workflow. Manual use:

```
./release.py <full zip> [--incremental <incremental zip>] [--recovery <lineage-<device>-recovery.tar.md5>]
```

Releases are tagged `<device>-<incremental>` and titled with the device name, so the wiki links each device to `releases?q=<device>-`. No release is marked latest, the releases page would otherwise show one device on top.
