[app]
# Brahim Onion Agent - Android APK Configuration
# Build with: buildozer android debug

title = Brahim Onion Agent
package.name = brahimonionagent
package.domain = com.brahimlaws

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.include_patterns = assets/*,images/*

version = 1.3.0

requirements = python3,kivy,pydantic,requests

orientation = portrait
fullscreen = 0

# Android permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# Android API levels
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a

# Android features
android.allow_backup = True
android.accept_sdk_license = True

# App icon and splash
icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/splash.png

# Python for Android
p4a.branch = master
p4a.bootstrap = sdl2

# iOS settings (for future)
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master

[buildozer]
log_level = 2
warn_on_root = 1
