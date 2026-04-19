#!/usr/bin/env python3
"""
setup_vendor.py - FIXED: Memisahkan Android.mk dan a02-vendor.mk
"""
import argparse
from pathlib import Path

CONFLICT_LIBS = {
    "android.hardware.camera.provider@2.4.so", "android.hardware.camera.provider@2.5.so",
    "android.hardware.camera.provider@2.6.so", "libalsautils.so", "libril.so",
    "libvpx.so", "libdrm.so", "libz.so", "libjpeg.so", "libpng.so"
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
    lines = [
        "LOCAL_PATH := $(call my-dir)",
        "",
        "include $(CLEAR_VARS)",
        "# File ini sengaja dikosongkan dari PRODUCT_COPY_FILES untuk fix readonly error",
        ""
    ]
    (dst / "Android.mk").write_text("\n".join(lines))

def write_vendor_mk(dst: Path, etc_files: list):
    # File ini yang bakal di-inherit di device/samsung/a02/arrow_a02.mk
    lines = [
        "# Vendor blobs copy files - SM-A022F",
        "PRODUCT_COPY_FILES += \\"
    ]
    entries = []
    for fname, rel_str in etc_files:
        entries.append(f"    vendor/samsung/a02/{rel_str}:$(TARGET_COPY_OUT_VENDOR)/{rel_str}")
    
    if entries:
        lines.append(" \\\n".join(entries))
    else:
        lines.append(" # No files to copy")
        
    (dst / "a02-vendor.mk").write_text("\n".join(lines))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--dst", required=True)
    args = ap.parse_args()

    dst = Path(args.dst).resolve()
    # Pastikan folder tujuan ada
    dst.mkdir(parents=True, exist_ok=True)
    
    all_files = [f for f in dst.rglob("*") if f.is_file()]
    so_libs = [f for f in all_files if f.suffix == ".so" and f.name not in CONFLICT_LIBS]
    etc_files = [(f.name, str(f.relative_to(dst))) for f in all_files if f.suffix != ".so" and f.name not in ["Android.bp", "Android.mk", "a02-vendor.mk"]]

    write_bp(dst, so_libs)
    write_mk(dst)
    write_vendor_mk(dst, etc_files)
    print("[+] Generated: Android.bp, Android.mk, and a02-vendor.mk")

if __name__ == "__main__":
    main()
