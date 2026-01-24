# Brahim Secure Intelligence - ProGuard Rules
# ==============================================
#
# Mathematical Foundation: beta = sqrt(5) - 2 = 1/phi^3

# Keep Brahim constants
-keep class com.brahim.bsi.core.BrahimConstants { *; }

# Keep data classes
-keep class com.brahim.bsi.cipher.WormholeResult { *; }
-keep class com.brahim.bsi.safety.SafetyAssessment { *; }
-keep class com.brahim.bsi.safety.SafetyVerdict { *; }
-keep class com.brahim.bsi.router.RoutingResult { *; }
-keep class com.brahim.bsi.router.Territory { *; }
-keep class com.brahim.bsi.agent.AgentResponse { *; }
-keep class com.brahim.bsi.agent.WavelengthState { *; }

# Keep enum values
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

# Optimization
-optimizationpasses 5
-dontusemixedcaseclassnames
-verbose

# Remove logging in release
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
}
