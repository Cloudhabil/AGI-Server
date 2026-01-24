/**
 * Brahim Secure Intelligence - Project Build Configuration
 *
 * Mathematical Foundation: beta = sqrt(5) - 2 = 1/phi^3
 */

plugins {
    id("com.android.application") version "8.2.2" apply false
    id("org.jetbrains.kotlin.android") version "1.9.22" apply false
}

tasks.register("clean", Delete::class) {
    delete(rootProject.layout.buildDirectory)
}
