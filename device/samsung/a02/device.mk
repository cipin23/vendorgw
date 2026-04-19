# Dynamic partitions
PRODUCT_USE_DYNAMIC_PARTITIONS := true

# Vendor blobs
$(call inherit-product, vendor/samsung/a02/Android.mk)

# HIDL / HAL manifests
DEVICE_MANIFEST_FILE := $(DEVICE_PATH)/manifest.xml
DEVICE_MATRIX_FILE   := $(DEVICE_PATH)/compatibility_matrix.xml

# Overlays
DEVICE_PACKAGE_OVERLAYS += $(DEVICE_PATH)/overlay

# Display
PRODUCT_AAPT_CONFIG  := normal
PRODUCT_AAPT_PREF_CONFIG := xhdpi

# RIL (DSDS)
PRODUCT_PACKAGES += \
    android.hardware.radio@1.4 \
    android.hardware.radio.config@1.2

# Telephony
PRODUCT_PACKAGES += \
    Stk \
    CellBroadcastReceiver

# Permissions
PRODUCT_COPY_FILES += \
    frameworks/native/data/etc/android.hardware.telephony.gsm.xml:$(TARGET_COPY_OUT_PRODUCT)/etc/permissions/android.hardware.telephony.gsm.xml \
    frameworks/native/data/etc/android.hardware.telephony.cdma.xml:$(TARGET_COPY_OUT_PRODUCT)/etc/permissions/android.hardware.telephony.cdma.xml \
    frameworks/native/data/etc/android.hardware.wifi.xml:$(TARGET_COPY_OUT_PRODUCT)/etc/permissions/android.hardware.wifi.xml \
    frameworks/native/data/etc/android.hardware.bluetooth.xml:$(TARGET_COPY_OUT_PRODUCT)/etc/permissions/android.hardware.bluetooth.xml \
    frameworks/native/data/etc/android.hardware.camera.xml:$(TARGET_COPY_OUT_PRODUCT)/etc/permissions/android.hardware.camera.xml \
    frameworks/native/data/etc/handheld_core_hardware.xml:$(TARGET_COPY_OUT_PRODUCT)/etc/permissions/handheld_core_hardware.xml

# Dual SIM
PRODUCT_COPY_FILES += \
    $(DEVICE_PATH)/configs/dual_sim.xml:$(TARGET_COPY_OUT_PRODUCT)/etc/permissions/dual_sim.xml

# Properties
PRODUCT_PROPERTY_OVERRIDES += \
    ro.telephony.sim.count=2 \
    persist.radio.multisim.config=dsds \
    ro.multi.rild=true \
    rild.libpath=/vendor/lib/libril-mtk.so \
    rild.libpath2=/vendor/lib/libril-mtk.so
