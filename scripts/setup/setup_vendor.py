#!/usr/bin/env python3
"""
setup_vendor.py - Generate Android.bp + Android.mk dari blobs lokal
--src dan --dst nunjuk ke folder yang SAMA (vendor/samsung/a02/)
Blobs udah ada di sana, script cuma generate manifest files
Usage: python3 setup_vendor.py --src <vendor/samsung/a02> --dst <vendor/samsung/a02>
"""

import argparse
from pathlib import Path

CONFLICT_LIBS = {
    # Camera HAL
    "android.hardware.camera.provider@2.4.so",
    "android.hardware.camera.provider@2.5.so",
    "android.hardware.camera.provider@2.6.so",
    # Audio
    "libalsautils.so",
    "libbluetooth_audio_session.so",
    "libdownmix.so",
    "libstagefright_amrnb_common.so",
    # RIL
    "libril.so",
    # Media / codec (ada di external/)
    "libvpx.so",
    "libdrm.so",
    "libopus.so",
    "libFLAC.so",
    "libaom.so",
    "libvorbisidec.so",
    "libwebm.so",
    "libspeex.so",
    "libgsm.so",
    "libogg.so",
    "libvorbis.so",
    "libxml2.so",
    "libexpat.so",
    "libz.so",
    "libjpeg.so",
    "libpng.so",
    "libgif.so",
    "libwebp.so",
    "libicuuc.so",
    "libicui18n.so",
    "libssl.so",
    "libcrypto.so",
    "libpcre.so",
    "libpcre2.so",
    "libsqlite.so",
    # Stagefright soft codecs (ada di frameworks/av)
    "libstagefright_soft_vpxdec.so",
    "libstagefright_soft_vpxenc.so",
    "libstagefright_soft_hevcdec.so",
    "libstagefright_soft_mpeg4dec.so",
    "libstagefright_soft_mpeg4enc.so",
    "libstagefright_soft_mp3dec.so",
    "libstagefright_soft_aacdec.so",
    "libstagefright_soft_aacenc.so",
    "libstagefright_soft_amrdec.so",
    "libstagefright_soft_amrnbenc.so",
    "libstagefright_soft_amrwbenc.so",
    "libstagefright_soft_avcdec.so",
    "libstagefright_soft_avcenc.so",
    "libstagefright_soft_flacdec.so",
    "libstagefright_soft_flacenc.so",
    "libstagefright_soft_g711dec.so",
    "libstagefright_soft_gsmdec.so",
    "libstagefright_soft_mpeg2dec.so",
    "libstagefright_soft_opusdec.so",
    "libstagefright_soft_rawdec.so",
    "libstagefright_soft_vorbisdec.so",
    "libstagefright_soft_ddpdec.so",
    "libstagefright_soft_ac4dec.so",
    "libstagefright_softomx.so",
    "libstagefright_softomx_plugin.so",
    "libstagefright_flacdec.so",
    "libstagefright_bufferpool@2.0.1.so",
    "libstagefright_bufferqueue_helper_vendor.so",
    "libstagefright_enc_common.so",
    "libstagefright_omx_vendor.so",
    "libstagefright_foundation.so",
    # Codec2
    "libcodec2_vndk.so",
    "libcodec2_hidl@1.1.so",
    "libcodec2_hidl@1.0.so",
    "libsfplugin_ccodec_utils.so",
    "libvkmanager_vendor.so",
}

SKIP_ETC = {
    "etc/init", "etc/selinux", "etc/group", "etc/passwd",
    "etc/fs_config_files", "etc/fs_config_dirs", "etc/vintf",
}

def is_conflict(filename):
    """Prefix semua lib dengan vendor_a02_ kecuali yang udah punya namespace unik"""
    stem = Path(filename).stem
    # Lib yang namanya udah unik (vendor-specific), gak perlu prefix
    SAFE_PREFIXES = (
        "vendor.samsung", "vendor.mediatek", "vendor_samsung", "vendor_mediatek",
        "libsec", "libsamsung", "libmtk", "libmedia_", "libril-mtk",
    )
    for p in SAFE_PREFIXES:
        if stem.startswith(p) or stem.startswith(p.replace(".", "_")):
            return False
    # Semua lib lain dapat prefix vendor_a02_
    return True

def should_skip_etc(rel_str):
    for skip in SKIP_ETC:
        if rel_str.startswith(skip):
            return True
    return False

def collect(root: Path):
    so_libs = []
    etc_files = []
    seen = set()

    for f in sorted(root.rglob("*")):
        if not f.is_file():
            continue
        try:
            rel = f.relative_to(root)
        except ValueError:
            continue
        rel_str = str(rel).replace("\\", "/")

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

def write_bp(dst: Path, so_libs: list):
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
            f'    srcs: ["{rel_str}"],',
            "    vendor: true,",
            "    strip: { none: true },",
            "    check_elf_files: false,",
            "    prefer: true,",
            "}",
            "",
        ]
    (dst / "Android.bp").write_text("\n".join(lines))
    print(f"[+] Android.bp: {len(so_libs)} libs")

def write_mk(dst: Path, etc_files: list):
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
            entries.append(f"    $(LOCAL_PATH)/{rel_str}:$(TARGET_COPY_OUT_VENDOR)/{rel_str}")
        lines.append(" \\\n".join(entries))
    lines.append("")
    (dst / "Android.mk").write_text("\n".join(lines))
    print(f"[+] Android.mk: {len(etc_files)} etc files")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="folder blobs (vendor/samsung/a02)")
    ap.add_argument("--dst", required=True, help="output folder (sama dengan --src)")
    args = ap.parse_args()

    src = Path(args.src).resolve()
    dst = Path(args.dst)
    dst.mkdir(parents=True, exist_ok=True)

    print(f"[*] Scanning blobs from: {src}")
    so_libs, etc_files = collect(src)
    print(f"[*] Found: {len(so_libs)} .so, {len(etc_files)} etc files")

    write_bp(dst, so_libs)
    write_mk(dst, etc_files)
    print("[*] Done.")

if __name__ == "__main__":
    main()
