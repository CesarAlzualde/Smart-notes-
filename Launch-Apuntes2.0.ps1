# Apuntes 2.0 - Launcher PowerShell Script
param(
    [switch]$SkipBackendCheck,
    [switch]$DevMode
)

# Configuración
$BackendPath = "backend\dist\ApuntesBackend\ApuntesBackend.exe"
$FrontendPath = "auth-frontend"
$BackendUrl = "http://localhost:5000"
$FrontendUrl = "http://localhost:5174"

# Colores para output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) { Write-Output $args }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-Host ""
Write-ColorOutput Green "=============================================";
Write-ColorOutput Green "      APUNTES 2.0 - SISTEMA DE NOTAS IA"
Write-ColorOutput Green "=============================================";
Write-Host ""

# Verificar backend existe
if (-not $SkipBackendCheck -and -not (Test-Path $BackendPath)) {
    Write-ColorOutput Red "❌ ERROR: Backend no encontrado en: $BackendPath"
    Write-ColorOutput Yellow "   Por favor ejecuta PyInstaller primero:"
    Write-ColorOutput Yellow "   cd backend && pyinstaller ApuntesBackend.spec"
    exit 1
}

# Función para verificar si un puerto está en uso
function Test-Port($port) {
    try {
        $listener = [System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties().GetActiveTcpListeners()
        return $listener | Where-Object { $_.Port -eq $port }
    } catch {
        return $false
    }
}

# Función para matar procesos si existen
function Stop-ProcessSafely($processName) {
    try {
        Get-Process -Name $processName -ErrorAction SilentlyContinue | Stop-Process -Force
        Write-ColorOutput Yellow "🔄 Proceso $processName detenido"
    } catch {
        # No hay problema si no existe
    }
}

# Limpiar procesos previos
Write-ColorOutput Cyan "[0/4] Limpiando procesos previos..."
Stop-ProcessSafely "ApuntesBackend"
Stop-ProcessSafely "node"
Start-Sleep -Seconds 2

# Paso 1: Iniciar Backend
Write-ColorOutput Cyan "[1/4] Iniciando backend Flask..."
if (-not $SkipBackendCheck) {
    $backendProcess = Start-Process -FilePath $BackendPath -WindowStyle Minimized -PassThru
    Write-ColorOutput Green "✅ Backend iniciado (PID: $($backendProcess.Id))"
} else {
    Write-ColorOutput Yellow "⚠️ Saltando inicio de backend (modo desarrollo)"
}

# Paso 2: Esperar backend
Write-ColorOutput Cyan "[2/4] Esperando a que el backend responda..."
$maxAttempts = 15
$attempt = 0
$backendReady = $false

while ($attempt -lt $maxAttempts -and -not $backendReady) {
    try {
        $response = Invoke-WebRequest -Uri $BackendUrl -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
            Write-ColorOutput Green "✅ Backend respondiendo correctamente"
        }
    } catch {
        $attempt++
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 2
    }
}

if (-not $backendReady) {
    Write-ColorOutput Yellow "⚠️ Backend podría no estar completamente listo"
    Write-ColorOutput Yellow "   Continuando de todos modos..."
}

# Paso 3: Iniciar Frontend
Write-ColorOutput Cyan "[3/4] Iniciando frontend React..."
if ($DevMode) {
    # Modo desarrollo - usar npm run dev
    Write-ColorOutput Yellow "🔧 Modo desarrollo activado"
    $frontendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "cd `"$FrontendPath`" && npm run dev" -WindowStyle Normal -PassThru
} else {
    # Modo producción - intentar construir y servir
    Write-ColorOutput Cyan "   Intentando construir frontend..."
    try {
        Set-Location $FrontendPath
        $buildResult = & npm run build 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput Green "✅ Frontend construido exitosamente"
            # Servir archivos estáticos
            $frontendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "cd build && python -m http.server 5174" -WindowStyle Minimized -PassThru
        } else {
            throw "Build failed"
        }
        Set-Location ..
    } catch {
        Write-ColorOutput Yellow "⚠️ No se pudo construir, usando modo desarrollo"
        $frontendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "cd `"$FrontendPath`" && npm run dev" -WindowStyle Normal -PassThru
    }
}

# Paso 4: Abrir navegador
Write-ColorOutput Cyan "[4/4] Abriendo navegador..."
Start-Sleep -Seconds 3
Start-Process $FrontendUrl

# Información final
Write-Host ""
Write-ColorOutput Green "=============================================";
Write-ColorOutput Green "        SISTEMA INICIADO EXITOSAMENTE"
Write-ColorOutput Green "=============================================";
Write-Host ""
Write-ColorOutput White "🌐 Frontend: $FrontendUrl"
Write-ColorOutput White "🔧 Backend:  $BackendUrl"
Write-Host ""
Write-ColorOutput Yellow "⚠️  IMPORTANTE: NO cierres esta ventana"
Write-ColorOutput Yellow "   Presiona Ctrl+C para cerrar la aplicación"
Write-Host ""

# Mantener vivo y manejar Ctrl+C
$exitRequested = $false
try {
    while (-not $exitRequested) {
        Start-Sleep -Seconds 5
        
        # Verificar si los procesos siguen vivos
        if ($backendProcess -and $backendProcess.HasExited) {
            Write-ColorOutput Red "❌ El backend se cerró inesperadamente"
            break
        }
        if ($frontendProcess -and $frontendProcess.HasExited) {
            Write-ColorOutput Red "❌ El frontend se cerró inesperadamente"
            break
        }
    }
} catch [System.Management.Automation.PipelineStoppedException] {
    # Ctrl+C presionado
    $exitRequested = $true
}

# Limpieza al salir
Write-ColorOutput Cyan "🔄 Cerrando aplicación..."
Stop-ProcessSafely "ApuntesBackend"
Stop-ProcessSafely "node"
Stop-ProcessSafely "python"

Write-ColorOutput Green "✅ Sistema cerrado exitosamente"
