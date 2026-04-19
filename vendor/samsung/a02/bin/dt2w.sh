#!/vendor/bin/sh

sleep 15

export PATH=/system/bin:/system/xbin:/system/system_ext/bin:/vendor/bin:$PATH

settings put global hide_error_dialogs 1

while true; do
    VAL=$(/system/bin/settings get secure double_tap_to_wake)
    
    if [ "$VAL" = "1" ]; then
        /system/bin/settings put secure wake_gesture_enable 1
        /system/bin/echo "aot_enable,1" > /sys/class/sec/tsp/cmd
        /system/bin/echo "double_tap_enable,1" > /sys/class/sec/tsp/cmd
    else
        /system/bin/settings put secure wake_gesture_enable 0
        /system/bin/echo "aot_enable,0" > /sys/class/sec/tsp/cmd
        /system/bin/echo "double_tap_enable,0" > /sys/class/sec/tsp/cmd
		/system/bin/echo "proximity_check,0" > /sys/class/sec/tsp/cmd
    fi
    
    sleep 3
done