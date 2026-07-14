[app]
title = HabitGraph
package.name = habitgraph
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 0.1.0
requirements = python3,kivy==2.3.1

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/icon.png

android.permissions = 
android.api = 33
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
