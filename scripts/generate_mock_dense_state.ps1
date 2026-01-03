param(
    [string]$TargetPath = ".\\memory\\dense\\state_vector.bin",
    [int]$Seed = 42
)

$rand = New-Object System.Random $Seed
$mockState = New-Object float[] 512

# LOGIC sector 128-255: high resonance
for ($i = 128; $i -lt 256; $i++) {
    $mockState[$i] = [float](0.8 + ($rand.NextDouble() * 0.2))
}

# Other sectors: low noise
for ($i = 0; $i -lt 512; $i++) {
    if ($i -lt 128 -or $i -ge 256) {
        $mockState[$i] = [float]($rand.NextDouble() * 0.1)
    }
}

$bytes = New-Object byte[] 2048
[Buffer]::BlockCopy($mockState, 0, $bytes, 0, $bytes.Length)

$targetDir = Split-Path -Parent $TargetPath
New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
[System.IO.File]::WriteAllBytes($TargetPath, $bytes)

Write-Output "Generated Dense-State at $TargetPath (2048 bytes)."
