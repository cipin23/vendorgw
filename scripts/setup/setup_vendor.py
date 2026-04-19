#!/usr/bin/env python3
import argparse
from pathlib import Path

# Daftar library yang biasanya bentrok sama AOSP/ArrowOS
CONFLICT_LIBS = {
    "libalsautils.so", "libril.so", "libvpx.so", "libdrm.so", "libz.so", 
    "libjpeg.so", "libpng.so", "libbase.so", "libc++.so"
}

def write_bp(dst: Path, so_libs: list):
    """Bikin Android.bp buat semua .so yang ketemu"""
    lines = ["// Auto-generated Vendor Blobs BP - SM-A022F", ""]
    for lib_rel_path in so_libs:
        # Pake nama file tanpa .so sebagai nama module, tambahin prefix biar aman
        mod_name = f"vendor_a02_{lib_rel_path.stem}"
        lines += [
            "cc_prebuilt_library_shared {",
            f'    name: "{mod_name}",',
            f'    srcs: ["{str(lib_rel_path)}"],',
            "    vendor: true,",
            "    strip: { none: true },",
            "    check_elf_files: false,",
            "    prefer: true,",
            "}", ""
        ]
    (dst / "Android.bp").write_text("\n".join(lines))
    print(f"[+] Android.bp generated with {len(so_libs)} modules.")

def write_vendor_mk(dst: Path, etc_files: list):
    """Bikin a02-vendor.mk buat copy file non-biner"""
    lines = [
        "# Auto-generated Vendor Copy Files",
        "PRODUCT_COPY_FILES += \\"
    ]
    entries = []
    for rel_path in etc_files:
        entries.append(f"    vendor/samsung/a02/{str(rel_path)}:$(TARGET_COPY_OUT_VENDOR)/{str(rel_path)}")
    
    if entries:
        lines.append(" \\\n".join(entries))
    else:
        lines.append("    # No files to copy")
        
    (dst / "a02-vendor.mk").write_text("\n".join(lines))
    print(f"[+] a02-vendor.mk generated with {len(etc_files)} files.")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="Path ke folder vendor/samsung/a02")
    args = ap.parse_args()

    # Kita kerja langsung di dalam folder vendor tersebut
    base_path = Path(args.src).resolve()
    
    if not base_path.exists():
        print(f"[!] Path {base_path} ga ketemu!")
        return

    # Scan semua file di dalam folder vendor
    all_files = [f for f in base_path.rglob("*") if f.is_file()]
    
    # Pisahin mana yang library (.so) mana yang file biasa (etc, bin, dll)
    # Kita skip file manifest yang mau kita bikin sendiri
    skip_names = ["Android.bp", "Android.mk", "a02-vendor.mk"]
    
    so_libs = []
    etc_files = []
    
    for f in all_files:
        rel = f.relative_to(base_path)
        if rel.name in skip_names:
            continue
            
        if f.suffix == ".so":
            if rel.name not in CONFLICT_LIBS:
                so_libs.append(rel)
        else:
            etc_files.append(rel)

    # Tulis file konfigurasinya
    write_bp(base_path, so_libs)
    write_vendor_mk(base_path, etc_files)
    
    # Bikin Android.mk kosong (cuma boilerplate)
    (base_path / "Android.mk").write_text("LOCAL_PATH := $(call my-dir)\n\ninclude $(CLEAR_VARS)\n")

if __name__ == "__main__":
    main()
