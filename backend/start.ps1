# StadiumIQ Backend Startup Script
$ErrorActionPreference = "Stop"

# Load environment variables from .env file
$envFile = Join-Path (Join-Path $PSScriptRoot "..") ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]*?)\s*=\s*(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
            Write-Host "Loaded: $name"
        }
    }
}

# Start uvicorn
Write-Host "Starting StadiumIQ Backend on http://localhost:8000"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
