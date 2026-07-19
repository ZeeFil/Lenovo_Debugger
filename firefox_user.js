// Firefox ESR RAM Optimization - user.js
// For Lenovo Smarthome Hub Tablet (4GB RAM, postmarketOS)
// This file goes in the Firefox profile directory

// === PROCESS MANAGEMENT ===
// Limit content processes to 2 (default 8) - saves ~400MB RAM
user_pref("dom.ipc.processCount", 2);
// Limit web extensions to 1 process
user_pref("extensions.webextensions.remote.process.limit", 1);

// === MEMORY CACHE LIMITS ===
// Cap memory cache to 32MB (default auto/512MB)
user_pref("browser.cache.memory.capacity", 32768);
// Cap media cache to 16MB (default 512MB)
user_pref("media.memory_cache_max_size", 16384);
// Limit image cache
user_pref("image.mem.max_decoded_image_kb", 51200);

// === TAB MANAGEMENT ===
// Unload tabs when memory is low
user_pref("browser.tabs.unloadOnLowMemory", true);
// Save session less frequently (60s vs 15s)
user_pref("browser.sessionstore.interval", 60000);
// Don't store excessive tab history
user_pref("browser.sessionhistory.max_entries", 10);

// === GPU / RENDERING ===
// Enable WebRender for GPU compositing (reduces CPU/RAM load)
user_pref("gfx.webrender.all", true);
// Use GPU process for compositing
user_pref("layers.gpu-process.enabled", true);
// Enable hardware video decoding
user_pref("media.ffmpeg.vaapi.enabled", true);
user_pref("media.hardware-video-decoding.enabled", true);

// === DISABLE UNNECESSARY FEATURES ===
// Disable Pocket
user_pref("extensions.pocket.enabled", false);
// Disable sponsored content
user_pref("browser.newtabpage.activity-stream.showSponsored", false);
user_pref("browser.newtabpage.activity-stream.showSponsoredTopSites", false);
// Disable Picture-in-Picture auto-show
user_pref("media.videocontrols.picture-in-picture.video-toggle.enabled", false);
// Disable Firefox accounts/sync prompt
user_pref("identity.fxaccounts.enabled", false);
// Disable crash reporter
user_pref("browser.crashReports.unsubmittedCheck.autoSubmit2", false);
// Disable telemetry
user_pref("toolkit.telemetry.enabled", false);
user_pref("toolkit.telemetry.unified", false);
user_pref("datareporting.healthreport.uploadEnabled", false);
// Disable prefetching (saves RAM and bandwidth)
user_pref("network.prefetch-next", false);
user_pref("network.dns.disablePrefetch", true);
user_pref("network.http.speculative-parallel-limit", 0);

// === TOUCH / MOBILE OPTIMIZATION ===
// Enable touch events
user_pref("dom.w3c_touch_events.enabled", 1);
// Enable pinch-to-zoom
user_pref("apz.allow_zooming", true);
user_pref("apz.allow_double_tap_zooming", true);
// Smooth scrolling with touch
user_pref("general.smoothScroll", true);
user_pref("general.smoothScroll.msdPhysics.enabled", true);

// === NETWORK / LOADING ===
// Reduce simultaneous connections (saves memory)
user_pref("network.http.max-persistent-connections-per-server", 4);
user_pref("network.http.max-connections", 48);
