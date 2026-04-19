#!/usr/bin/env python3
"""
setup_vendor.py - FIXED: Memisahkan Android.mk dan Product Copy Files
"""
import argparse
from pathlib import Path

CONFLICT_LIBS = {
    "android.hardware.camera.provider@2.4.so", "libalsautils.so", "libril.so",
    "libvpx.so", "libdrm.so", "libz.so", "libjpeg.so"
}

def write_bp(dst: Path, so_libs: list):
    lines = ["// Auto-generated - Vendor Blobs BP", ""]
    for lib in so_libs:
        lines += [
            "cc_prebuilt_library_shared {",
            f'    name: "vendor_a02_{lib.stem}",',
            f'    srcs: ["{lib.name}"],',
            "    vendor: true,",
            "    strip: { none: true },",
            "    check_elf_files: false,",
            "    prefer: true,",
            "}", ""
        ]
    (dst / "Android.bp").write_text("\n".join(lines))

def write_mk(dst: Path):
    # Android.mk sekarang cuma buat include sub-dirs atau modul, bukan copy files
    lines = [
        "LOCAL_PATH := $(call my-dir)",
        "",
        "include $(CLEAR_VARS)",
        "# Kosongkan dari PRODUCT_COPY_FILES untuk menghindari error readonly",
        ""
    ]
    (dst / "Android.mk").write_text("\n".join(lines))

def write_vendor_mk(dst: Path, etc_files: list):
    # File ini yang bakal di-inherit oleh device tree
    lines = [
        "# Vendor blobs copy files - SM-A022F",
        "PRODUCT_COPY_FILES += \\"
    ]
    entries = []
    for fname, rel_str in etc_files:
        entries.append(f"    vendor/samsung/a02/{rel_str}:$(TARGET_COPY_OUT_VENDOR)/{rel_str}")
    lines.append(" \\\n".join(entries))
    (dst / "a02-vendor.mk").write_text("\n".join(lines))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--dst", required=True)
    args = ap.parse_args()

    dst = Path(args.dst).resolve()
    all_files = list(dst.rglob("*"))
    so_libs = [f for f in all_files if f.suffix == ".so" and f.name not in CONFLICT_LIBS]
    etc_files = [(f.name, str(f.relative_to(dst))) for f in all_files if f.is_file() and f.suffix != ".so"]

    write_bp(dst, so_libs)
    write_mk(dst)
    write_vendor_mk(dst, etc_files)
    print("[+] Generated: Android.bp, Android.mk, and a02-vendor.mk")

if __name__ == "__main__":
    main()
