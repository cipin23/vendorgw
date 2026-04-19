#!/usr/bin/env python3
"""
gen_device_tree.py - Generate device/samsung/a02/ skeleton for MT6739 ArrowOS 11
"""

import os, argparse
from pathlib import Path

# ── Device constants ──────────────────────────────────────────────────────────
DEVICE_VARS = {
    "DEVICE_PATH":            "device/samsung/a02",
    "BOARD_VENDOR":           "samsung",
    "TARGET_DEVICE":          "a02",
    "TARGET_PRODUCT":         "arrow_a02",
    "PRODUCT_MANUFACTURER":   "samsung",
    "PRODUCT_BRAND":          "samsung",
    "PRODUCT_MODEL":          "SM-A022F",
    "PRODUCT_NAME":           "arrow_a02",
    "TARGET_BOARD_PLATFORM":  "mt6739",
    "TARGET_BOOTLOADER_BOARD_NAME": "k39tv1_bsp_titan_hamster",
    "TARGET_NO_BOOTLOADER":   "true",
    # ARM 32-bit
    "TARGET_ARCH":            "arm",
    "TARGET_ARCH_VARIANT":    "armv8-a",
    "TARGET_CPU_ABI":         "armeabi-v7a",
    "TARGET_CPU_ABI2":        "armeabi",
    "TARGET_CPU_VARIANT":     "cortex-a53",
    # Kernel
    "BOARD_KERNEL_BASE":      "0x40000000",
    "BOARD_KERNEL_PAGESIZE":  "2048",
    "BOARD_RAMDISK_OFFSET":   "0x11b00000",
    "BOARD_KERNEL_TAGS_OFFSET":"0x07880000",
    "BOARD_BOOT_HEADER_VERSION":"2",
    "BOARD_KERNEL_IMAGE_NAME":"zImage",
    "TARGET_PREBUILT_KERNEL": "device/samsung/a02/prebuilt/zImage",
    "BOARD_KERNEL_CMDLINE":   "bootopt=64S3,32S1,32S1 androidboot.selinux=permissive",
    # Partitions - dynamic
    "BOARD_SUPER_PARTITION_SIZE":       "1610612736",
    "BOARD_SUPER_PARTITION_GROUPS":     "samsung_dynamic_partitions",
    "BOARD_SAMSUNG_DYNAMIC_PARTITIONS_PARTITION_LIST": "system vendor product",
    "BOARD_SAMSUNG_DYNAMIC_PARTITIONS_SIZE":           "1606418432",
    "BOARD_SYSTEMIMAGE_PARTITION_RESERVED_SIZE":       "104857600",
    "BOARD_USERDATAIMAGE_FILE_SYSTEM_TYPE": "f2fs",
    "BOARD_SYSTEMIMAGE_FILE_SYSTEM_TYPE":   "ext4",
    "BOARD_VENDORIMAGE_FILE_SYSTEM_TYPE":   "ext4",
    "BOARD_PRODUCTIMAGE_FILE_SYSTEM_TYPE":  "ext4",
    "TARGET_COPY_OUT_VENDOR": "vendor",
    "TARGET_COPY_OUT_PRODUCT":"product",
    # AVB
    "BOARD_AVB_ENABLE":       "true",
    "BOARD_AVB_MAKE_VBMETA_IMAGE_ARGS": "--flags 3",
    # Recovery
    "BOARD_HAS_LARGE_FILESYSTEM": "true",
    "TARGET_RECOVERY_PIXEL_FORMAT": "RGBX_8888",
    # Display
    "TARGET_SCREEN_DENSITY":  "300",
    # VINTF
    "DEVICE_MANIFEST_FILE":   "$(DEVICE_PATH)/manifest.xml",
    "DEVICE_MATRIX_FILE":     "$(DEVICE_PATH)/compatibility_matrix.xml",
}

PRODUCT_MK = """\
# Inherit AOSP
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/product_launched_with_p.mk)

# Inherit device
$(call inherit-product, $(LOCAL_PATH)/device.mk)

# Inherit ArrowOS
$(call inherit-product, vendor/arrow/config/common_full_phone.mk)

PRODUCT_DEVICE := a02
PRODUCT_NAME   := arrow_a02
PRODUCT_BRAND  := samsung
PRODUCT_MODEL  := SM-A022F
PRODUCT_MANUFACTURER := samsung

PRODUCT_GMS_CLIENTID_BASE := android-samsung
TARGET_VENDOR_PRODUCT_NAME := a02

PRODUCT_BUILD_PROP_OVERRIDES += \\
    PRIVATE_BUILD_DESC="a02-user 11 RP1A.200720.012 A022FXXU3BVB1 release-keys" \\
    BUILD_FINGERPRINT="samsung/a02/a02:11/RP1A.200720.012/A022FXXU3BVB1:user/release-keys"
"""

DEVICE_MK = """\
# Dynamic partitions
PRODUCT_USE_DYNAMIC_PARTITIONS := true

# Vendor blobs
$(call inherit-product, vendor/samsung/a02/Android.mk)

# HIDL / HAL manifests
DEVICE_MANIFEST_FILE := $(DEVICE_PATH)/manifest.xml
DEVICE_MATRIX_FILE   := $(DEVICE_PATH)/compatibility_matrix.xml

# Display
PRODUCT_AAPT_CONFIG  := normal
PRODUCT_AAPT_PREF_CONFIG := xhdpi

# RIL (DSDS)
PRODUCT_PACKAGES += \\
    android.hardware.radio@1.4 \\
    android.hardware.radio.config@1.2

# Telephony
PRODUCT_PACKAGES += \\
    Stk \\
    CellBroadcastReceiver

# Permissions
PRODUCT_COPY_FILES += \\
    frameworks/native/data/etc/android.hardware.telephony.gsm.xml:$(TARGET_COPY_OUT_PRODUCT)/etc/permissions/android.hardware.telephony.gsm.xml \\
    frameworks/native/data/etc/android.hardware.telephony.cdma.xml:$(TARGET_COPY_OUT_PRODUCT)/etc/permissions/android.hardware.telephony.cdma.xml \\
    frameworks/native/data/etc/android.hardware.wifi.xml:$(TARGET_COPY_OUT_PRODUCT)/etc/permissions/android.hardware.wifi.xml \\
    frameworks/native/data/etc/android.hardware.bluetooth.xml:$(TARGET_COPY_OUT_PRODUCT)/etc/permissions/android.hardware.bluetooth.xml \\
    frameworks/native/data/etc/android.hardware.camera.xml:$(TARGET_COPY_OUT_PRODUCT)/etc/permissions/android.hardware.camera.xml \\
    frameworks/native/data/etc/handheld_core_hardware.xml:$(TARGET_COPY_OUT_PRODUCT)/etc/permissions/handheld_core_hardware.xml

# Dual SIM
PRODUCT_COPY_FILES += \\
    $(DEVICE_PATH)/configs/dual_sim.xml:$(TARGET_COPY_OUT_PRODUCT)/etc/permissions/dual_sim.xml

# Properties
PRODUCT_PROPERTY_OVERRIDES += \\
    ro.telephony.sim.count=2 \\
    persist.radio.multisim.config=dsds \\
    ro.multi.rild=true \\
    rild.libpath=/vendor/lib/libril-mtk.so \\
    rild.libpath2=/vendor/lib/libril-mtk.so
"""

BOARDCONFIG_MK = """\
# Inherit MediaTek common
-include vendor/samsung/a02/BoardConfigVendor.mk

DEVICE_PATH := device/samsung/a02

TARGET_BOARD_PLATFORM := mt6739
TARGET_BOOTLOADER_BOARD_NAME := k39tv1_bsp_titan_hamster
TARGET_NO_BOOTLOADER := true

# Binder
TARGET_USES_64_BIT_BINDER := true

# ARM 32-bit (NO lib64)
TARGET_ARCH         := arm
TARGET_ARCH_VARIANT := armv8-a
TARGET_CPU_ABI      := armeabi-v7a
TARGET_CPU_ABI2     := armeabi
TARGET_CPU_VARIANT  := cortex-a53
TARGET_2ND_ARCH     :=

# Kernel
BOARD_KERNEL_BASE        := 0x40000000
BOARD_KERNEL_PAGESIZE    := 2048
BOARD_RAMDISK_OFFSET     := 0x11b00000
BOARD_KERNEL_TAGS_OFFSET := 0x07880000
BOARD_BOOT_HEADER_VERSION := 2
BOARD_KERNEL_IMAGE_NAME  := zImage
TARGET_PREBUILT_KERNEL   := $(DEVICE_PATH)/prebuilt/zImage
BOARD_MKBOOTIMG_ARGS     := --ramdisk_offset $(BOARD_RAMDISK_OFFSET) \\
                            --tags_offset $(BOARD_KERNEL_TAGS_OFFSET) \\
                            --header_version $(BOARD_BOOT_HEADER_VERSION)
BOARD_KERNEL_CMDLINE     := bootopt=64S3,32S1,32S1 androidboot.selinux=permissive

# Partitions
BOARD_FLASH_BLOCK_SIZE   := 131072
BOARD_SUPER_PARTITION_SIZE := 1610612736
BOARD_SUPER_PARTITION_GROUPS := samsung_dynamic_partitions
BOARD_SAMSUNG_DYNAMIC_PARTITIONS_PARTITION_LIST := system vendor product
BOARD_SAMSUNG_DYNAMIC_PARTITIONS_SIZE := 1606418432
BOARD_SYSTEMIMAGE_PARTITION_RESERVED_SIZE := 104857600
BOARD_USERDATAIMAGE_FILE_SYSTEM_TYPE := f2fs
BOARD_SYSTEMIMAGE_FILE_SYSTEM_TYPE  := ext4
BOARD_VENDORIMAGE_FILE_SYSTEM_TYPE  := ext4
BOARD_PRODUCTIMAGE_FILE_SYSTEM_TYPE := ext4
TARGET_COPY_OUT_VENDOR  := vendor
TARGET_COPY_OUT_PRODUCT := product

# AVB
BOARD_AVB_ENABLE := true
BOARD_AVB_MAKE_VBMETA_IMAGE_ARGS += --flags 3

# Recovery
BOARD_HAS_LARGE_FILESYSTEM := true
TARGET_RECOVERY_PIXEL_FORMAT := RGBX_8888
TARGET_USERIMAGES_USE_EXT4 := true
TARGET_USERIMAGES_USE_F2FS := true

# SELinux (permissive for dev)
SELINUX_IGNORE_NEVERALLOWS := true
BOARD_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy/vendor

# HIDL
DEVICE_MANIFEST_FILE    := $(DEVICE_PATH)/manifest.xml
DEVICE_MATRIX_FILE      := $(DEVICE_PATH)/compatibility_matrix.xml
"""

MANIFEST_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<manifest version="1.0" type="device" target-level="4">
    <hal format="hidl">
        <name>android.hardware.audio</name>
        <transport>hwbinder</transport>
        <version>6.0</version>
        <interface>
            <name>IDevicesFactory</name>
            <instance>default</instance>
        </interface>
    </hal>
    <hal format="hidl">
        <name>android.hardware.camera.provider</name>
        <transport>hwbinder</transport>
        <version>2.4</version>
        <interface>
            <name>ICameraProvider</name>
            <instance>legacy/0</instance>
        </interface>
    </hal>
    <hal format="hidl">
        <name>android.hardware.graphics.composer</name>
        <transport>hwbinder</transport>
        <version>2.1</version>
        <interface>
            <name>IComposer</name>
            <instance>default</instance>
        </interface>
    </hal>
    <hal format="hidl">
        <name>android.hardware.graphics.allocator</name>
        <transport>hwbinder</transport>
        <version>2.0</version>
        <interface>
            <name>IAllocator</name>
            <instance>default</instance>
        </interface>
    </hal>
    <hal format="hidl">
        <name>android.hardware.health</name>
        <transport>hwbinder</transport>
        <version>2.0</version>
        <interface>
            <name>IHealth</name>
            <instance>default</instance>
        </interface>
    </hal>
    <hal format="hidl">
        <name>android.hardware.radio</name>
        <transport>hwbinder</transport>
        <version>1.4</version>
        <interface>
            <name>IRadio</name>
            <instance>slot1</instance>
            <instance>slot2</instance>
        </interface>
    </hal>
    <hal format="hidl">
        <name>android.hardware.radio.config</name>
        <transport>hwbinder</transport>
        <version>1.2</version>
        <interface>
            <name>IRadioConfig</name>
            <instance>default</instance>
        </interface>
    </hal>
    <hal format="hidl">
        <name>android.hardware.wifi</name>
        <transport>hwbinder</transport>
        <version>1.3</version>
        <interface>
            <name>IWifi</name>
            <instance>default</instance>
        </interface>
    </hal>
    <hal format="hidl">
        <name>android.hardware.bluetooth</name>
        <transport>hwbinder</transport>
        <version>1.1</version>
        <interface>
            <name>IBluetoothHci</name>
            <instance>default</instance>
        </interface>
    </hal>
    <sepolicy>
        <version>29.0</version>
    </sepolicy>
</manifest>
"""

COMPAT_MATRIX_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<compatibility-matrix version="1.0" type="device" level="4">
    <hal format="hidl" optional="false">
        <name>android.hardware.audio</name>
        <version>6.0</version>
        <interface>
            <name>IDevicesFactory</name>
            <instance>default</instance>
        </interface>
    </hal>
    <hal format="hidl" optional="true">
        <name>android.hardware.camera.provider</name>
        <version>2.4-6</version>
        <interface>
            <name>ICameraProvider</name>
            <instance>legacy/0</instance>
        </interface>
    </hal>
    <hal format="hidl" optional="false">
        <name>android.hardware.health</name>
        <version>2.0-1</version>
        <interface>
            <name>IHealth</name>
            <instance>default</instance>
        </interface>
    </hal>
    <sepolicy>
        <kernel-sepolicy-version>30</kernel-sepolicy-version>
        <sepolicy-version>29.0</sepolicy-version>
    </sepolicy>
    <avb>
        <vbmeta-version>2.0</vbmeta-version>
    </avb>
</compatibility-matrix>
"""

ARROW_MK = """\
# Arrow product
TARGET_BOOT_ANIMATION_RES := 720
TARGET_SCREEN_HEIGHT := 1560
TARGET_SCREEN_WIDTH  := 720
TARGET_SUPPORTS_GOOGLE_SERVICES := false
"""

def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"[+] {path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vendor-src", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out = Path(args.out)

    write(out / "AndroidProducts.mk",
          f"PRODUCT_MAKEFILES := $(LOCAL_DIR)/arrow_a02.mk\n"
          f"COMMON_LUNCH_CHOICES := arrow_a02-user arrow_a02-userdebug arrow_a02-eng\n")

    write(out / "arrow_a02.mk",    PRODUCT_MK)
    write(out / "device.mk",       DEVICE_MK)
    write(out / "BoardConfig.mk",  BOARDCONFIG_MK)
    write(out / "manifest.xml",    MANIFEST_XML)
    write(out / "compatibility_matrix.xml", COMPAT_MATRIX_XML)
    write(out / "arrow.mk",        ARROW_MK)

    # Placeholder prebuilt dir (zImage will be symlinked/copied from release)
    (out / "prebuilt").mkdir(exist_ok=True)
    (out / "prebuilt" / ".gitkeep").touch()

    # Minimal sepolicy
    (out / "sepolicy" / "vendor").mkdir(parents=True, exist_ok=True)
    write(out / "sepolicy" / "vendor" / "file_contexts",
          "# vendor sepolicy for a02\n")

    # Overlay
    (out / "overlay" / "frameworks" / "base" / "core" / "res" / "res" / "values").mkdir(parents=True, exist_ok=True)
    write(out / "overlay" / "frameworks" / "base" / "core" / "res" / "res" / "values" / "config.xml",
          '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
          '    <integer name="config_screenDensityDpi">300</integer>\n'
          '    <bool name="config_mobile_data_capable">true</bool>\n'
          '    <bool name="config_sms_capable">true</bool>\n'
          '    <integer name="config_sim_count">2</integer>\n'
          '</resources>\n')

    # Dual SIM permission
    write(out / "configs" / "dual_sim.xml",
          '<?xml version="1.0" encoding="utf-8"?>\n'
          '<permissions>\n'
          '    <feature name="android.hardware.telephony.gsm" />\n'
          '    <feature name="android.hardware.telephony.cdma" />\n'
          '</permissions>\n')

    print(f"\n[*] Device tree generated at {out}")

if __name__ == "__main__":
    main()
