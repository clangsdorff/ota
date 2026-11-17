# ota

Updater feed for langsdorff builds. Devices fetch `<device>.json`.

Publishing a release with a `lineage-*.zip` asset updates the feed through the
`feed` workflow. Manual use:

```
./release.py <full zip>
```
