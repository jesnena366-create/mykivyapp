[app]
title = My Kivy App
package.name = mykivyapp
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_dirs = tests
source.exclude_globs = .github
requirements = python3,kivy
version = 0.1
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[app:android]
api = 33
minapi = 21
archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
