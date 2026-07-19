#!/bin/sh
# Optimized Firefox ESR launcher for Lenovo Smarthome Hub Tablet
# Configures Wayland, touch support, and memory optimization

# --- Wayland Native Rendering ---
export MOZ_ENABLE_WAYLAND=1
export GDK_BACKEND=wayland

# --- Touch Input Support ---
export MOZ_USE_XINPUT2=1

# --- Memory Optimization ---
# Reduce IPC shared memory usage
export MOZ_DISABLE_CONTENT_SANDBOX=0

# --- GPU Acceleration ---
# Enable hardware acceleration via Mesa/Panfrost
export LIBVA_DRIVER_NAME=radeonsi
export MOZ_WEBRENDER=1

# --- Launch Firefox ESR ---
exec firefox-esr "$@"
