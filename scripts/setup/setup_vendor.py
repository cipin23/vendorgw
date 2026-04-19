#!/usr/bin/env python3
"""
setup_vendor.py - Generate vendor/samsung/a02/Android.bp + Android.mk
Blobs TIDAK dicopy - path di Android.bp/mk nunjuk ke vendor/ root langsung
Usage: python3 setup_vendor.py --src <repo_root> --dst <vendor/samsung/a02>
"""

import argparse
from pathlib import Path

CONFLICT_LIBS = {
    "android.hardware.camera.provider@2.4.so",
    "android.hardware.camera.provider@2.5.so",
    "android.hardware.camera.provider@2.6.so",
    "libalsautils.so",
    "libbluetooth_audio_session.so",
    "libdownmix.so",
    "libril.so",
    "libstagefright_amrnb_common.so",
}

SKIP_ETC = {
    "etc/init", "etc/selinux", "etc/group", "etc/passwd",
    "etc/fs_config_files", "etc/fs_config_dirs", "etc/vintf",
}

def is_conflict(filename):
    return filename in CONFLICT_LIBS

def should_skip_etc(rel_str):
    for skip in SKIP_ETC:
        if rel_str.startswith(skip):
            return True
    return False

def collect(vendor_root: Path):
    so_libs = []
    etc_files = []
    seen = set()

    for f in sorted(vendor_root.rglob("*")):
        if not f.is_file():
            continue
        try:
            rel = f.relative_to(vendor_root)
        except ValueError:
            continue
        rel_str = str(rel).replace("\\", "/")

        if rel_str.startswith("samsung/"):
            continue
        if f.name in ("Android.bp", "Android.mk"):
            continue
        if f.name in seen:
            continue
        seen.add(f.name)

        if f.suffix == ".so":
            so_libs.append((f.name, rel_str))
        elif rel_str.startswith("etc/") and not should_skip_etc(rel_str):
            etc_files.append((f.name, rel_str))

    return so_libs, etc_files

def write_bp(dst: Path, so_libs: list, prefix: str):
    lines = [
        "// AUTO-GENERATED - DO NOT EDIT",
        'soong_namespace {}',
        "",
    ]
    for fname, rel_str in so_libs:
        stem = Path(fname).stem
        module_name = f"vendor_a02_{stem}" if is_conflict(fname) else stem
        lines += [
            "cc_prebuilt_library_shared {",
            f'    name: "{module_name}",',
            f'    srcs: ["{prefix}{rel_str}"],',
            "    vendor: true,",
            "    strip: { none: true },",
            "    check_elf_files: false,",
            "    prefer: true,",
            "}",
            "",
        ]
    (dst / "Android.bp").write_text("\n".join(lines))
    print(f"[+] Android.bp: {len(so_libs)} libs")

def write_mk(dst: Path, etc_files: list, prefix: str):
    lines = [
        "LOCAL_PATH := $(call my-dir)",
        "",
        "# Vendor blobs - SM-A022F MT6739",
        "# AUTO-GENERATED - DO NOT EDIT",
        "",
    ]
    if etc_files:
        lines.append("PRODUCT_COPY_FILES += \\")
        entries = []
        for fname, rel_str in etc_files:
            entries.append(f"    $(LOCAL_PATH)/{prefix}{rel_str}:$(TARGET_COPY_OUT_VENDOR)/{rel_str}")
        lines.append(" \\\n".join(entries))
    lines.append("")
    (dst / "Android.mk").write_text("\n".join(lines))
    print(f"[+] Android.mk: {len(etc_files)} etc files")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="repo root (contains vendor/)")
    ap.add_argument("--dst", required=True, help="output: vendor/samsung/a02")
    args = ap.parse_args()

    src = Path(args.src).resolve()
    dst = Path(args.dst)
    dst.mkdir(parents=True, exist_ok=True)

    vendor_root = src / "vendor"
    if not vendor_root.exists():
        print(f"[!] vendor/ not found in {src}")
        raise SystemExit(1)

    # dst = vendor/samsung/a02, vendor/ ada di ../../ dari sini
    prefix = "../../"

    print(f"[*] vendor root : {vendor_root}")
    print(f"[*] dst         : {dst}")
    print(f"[*] prefix      : {prefix}")

    so_libs, etc_files = collect(vendor_root)
    print(f"[*] Found: {len(so_libs)} .so, {len(etc_files)} etc files")

    write_bp(dst, so_libs, prefix)
    write_mk(dst, etc_files, prefix)

    print("[*] Done. No blobs copied.")

if __name__ == "__main__":
    main()
