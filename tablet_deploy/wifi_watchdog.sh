#!/bin/sh
# Lenovo Tablet Wi-Fi Watchdog - Hardened Edition

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 4. Boot Race Condition Fix
log "Starting Wi-Fi Watchdog. Waiting 60s for boot stabilization..."
sleep 60

FAIL_COUNT=0
MAX_FAILS=3
BASE_SLEEP=60
BACKOFF_MULTIPLIER=1
CURRENT_SLEEP=$BASE_SLEEP

while true; do
    # 8. Dynamic Interface Detection
    WLAN_IF=$(ip -o link show | awk -F': ' '{print $2}' | grep -E '^wl' | head -n1)
    
    # 1. & 2. Find local default gateway (instead of internet IP)
    TARGET_IP=$(ip route | grep default | awk '{print $3}' | head -n1)
    
    if [ -z "$TARGET_IP" ] || [ -z "$WLAN_IF" ]; then
        log "No default gateway or wlan interface found! Forcing immediate recovery."
        FAIL_COUNT=$MAX_FAILS
    else
        # 6. Strict timeout on ping (2 seconds)
        if ping -c 1 -W 2 -w 2 "$TARGET_IP" > /dev/null 2>&1; then
            FAIL_COUNT=0
            BACKOFF_MULTIPLIER=1
            CURRENT_SLEEP=$BASE_SLEEP
        else
            FAIL_COUNT=$((FAIL_COUNT + 1))
            log "Network ping to $TARGET_IP failed. Consecutive failures: $FAIL_COUNT"
        fi
    fi

    if [ "$FAIL_COUNT" -ge "$MAX_FAILS" ]; then
        log "Network stuck! Initiating full hardware recovery."
        
        # 3. RFKill Blocking Fix
        rfkill unblock wlan || true
        
        # 7. NetworkManager vs ip-link fallback
        log "Restarting NetworkManager..."
        if ! systemctl restart NetworkManager; then
            log "NetworkManager restart failed! Falling back to ip link toggle on ${WLAN_IF:-wlan0}..."
            ip link set "${WLAN_IF:-wlan0}" down
            sleep 2
            ip link set "${WLAN_IF:-wlan0}" up
        fi
        
        # 5. Exponential Backoff (Cap at ~16 minutes)
        if [ "$BACKOFF_MULTIPLIER" -lt 16 ]; then
            BACKOFF_MULTIPLIER=$((BACKOFF_MULTIPLIER * 2))
        fi
        CURRENT_SLEEP=$((BASE_SLEEP * BACKOFF_MULTIPLIER))
        
        log "Recovery triggered. Sleeping for $CURRENT_SLEEP seconds before next check to save battery."
        sleep 30 # Initial network recovery time
        FAIL_COUNT=0
    fi

    sleep "$CURRENT_SLEEP"
done
