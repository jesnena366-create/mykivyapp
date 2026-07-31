[app]
title = Network Probe
package.name = mykivyapp
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.3.0
orientation = portrait
fullscreen = 0

android.api = 34
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True
android.permissions = INTERNET,ACCESS_NETWORK_STATE
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 0
