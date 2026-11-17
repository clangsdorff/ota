# ota

Updater feed for langsdorff builds. Devices fetch `<device>/<incremental>.json`.

Keep `out/target/product/<device>/obj/PACKAGING/target_files_intermediates/*-target_files*.zip`
of every release; the next incremental is built from it.

```
ota_from_target_files -i <previous target_files> <new target_files> <incremental zip>
./release.py <full zip> [--incremental <incremental zip>]
```

Then create the printed release, commit and push the json files.
