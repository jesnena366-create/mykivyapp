[app]
title = Network Probe
package.name = mykivyapp
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
requirements = python3,kivy
version = 0.1
orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.permissions = INTERNET, ACCESS_NETWORK_STATE

[buildozer]
log_level = 2
warn_on_root = 0
