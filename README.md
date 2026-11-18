# ota

Updater feed for langsdorff builds. Devices fetch `<device>/<incremental>.json` and fall back to `<device>.json` for full updates.

Publishing a release with `lineage-*.zip` assets updates the feed through the `feed` workflow. Releases tagged `target-files-*` are ignored by the workflow. Manual use:

```
./release.py <full zip> [--incremental <incremental zip>]
```
