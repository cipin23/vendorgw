#!/usr/bin/env python3
import argparse, shutil
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
    lines = ["LOCAL_PATH := $(call my-dir)", "", "include $(CLEAR_VARS)", ""]
    (dst / "Android.mk").write_text("\n".join(lines))

def write_vendor_mk(dst: Path, etc_files: list):
    lines = ["# Vendor blobs copy files", "PRODUCT_COPY_FILES += \\"]
    entries = [f"    vendor/samsung/a02/{rel}:$(TARGET_COPY_OUT_VENDOR)/{rel}" for rel in etc_files]
    lines.append(" \\\n".join(entries) if entries else " # No files")
    (dst / "a02-vendor.mk").write_text("\n".join(lines))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True) # Folder hasil clone (vendor_src)
    ap.add_argument("--dst", required=True) # Folder tujuan (out_repo/vendor/...)
    args = ap.parse_args()

    src = Path(args.src).resolve()
    dst = Path(args.dst).resolve()
    dst.mkdir(parents=True, exist_ok=True)

    # 1. Copy semua file dari src ke dst (kecuali junk git)
    for f in src.rglob("*"):
        if f.is_file() and ".git" not in f.parts:
            rel_path = f.relative_to(src)
            target = dst / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)

    # 2. List file buat generate .mk & .bp
    all_files = [f.relative_to(dst) for f in dst.rglob("*") if f.is_file()]
    so_libs = [f for f in all_files if f.suffix == ".so" and f.name not in CONFLICT_LIBS]
    etc_files = [str(f) for f in all_files if f.suffix != ".so" and f.name not in ["Android.bp", "Android.mk", "a02-vendor.mk"]]

    write_bp(dst, so_libs)
    write_mk(dst)
    write_vendor_mk(dst, etc_files)
    print(f"[+] Done. Copied files and generated configs in {dst}")

if __name__ == "__main__":
    main()
