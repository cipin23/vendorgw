# Vendor blobs copy files - SM-A022F (MT6739)
# Manual fix to prevent readonly PRODUCT_COPY_FILES error

PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/etc/vintf/manifest.xml:$(TARGET_COPY_OUT_VENDOR)/etc/vintf/manifest.xml \
    $(LOCAL_PATH)/etc/prop.default:$(TARGET_COPY_OUT_VENDOR)/etc/prop.default \
    $(LOCAL_PATH)/firmware/mt6739_dsp.bin:$(TARGET_COPY_OUT_VENDOR)/firmware/mt6739_dsp.bin \
    $(LOCAL_PATH)/firmware/mt6739_scp.img:$(TARGET_COPY_OUT_VENDOR)/firmware/mt6739_scp.img \
    $(LOCAL_PATH)/overlay/framework-res__auto_generated_rro_vendor.apk:$(TARGET_COPY_OUT_VENDOR)/overlay/framework-res__auto_generated_rro_vendor.apk

# Tambahin file etc lainnya dari vendor_src loe ke sini kalo perlu
