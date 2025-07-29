# Script para probar autenticación y acceso a endpoints protegidos
Write-Host "1. Iniciando prueba de login..." -ForegroundColor Cyan

$loginData = @{
    email = "test@example.com"
    password = "password123"
} | ConvertTo-Json

Write-Host "Intentando login con credenciales de prueba..." -ForegroundColor Yellow
try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" -Method Post -Body $loginData -ContentType "application/json"
    Write-Host "Login exitoso!" -ForegroundColor Green
    
    # Extraer el token real
    $token = $loginResponse.access_token
    Write-Host "Token obtenido (primeros 20 caracteres): $($token.Substring(0, 20))..." -ForegroundColor Green
    
    # Crear headers con el token
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    
    Write-Host "`n2. Probando acceso a endpoint protegido..." -ForegroundColor Cyan
    Write-Host "Accediendo a /api/users/profile con el token..." -ForegroundColor Yellow
    
    try {
        $profileResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/users/profile" -Method Get -Headers $headers
        Write-Host "Acceso exitoso a perfil de usuario!" -ForegroundColor Green
        Write-Host "Datos del perfil:" -ForegroundColor White
        $profileResponse | Format-List
    }
    catch {
        Write-Host "Error al acceder al perfil: $_" -ForegroundColor Red
        Write-Host "Respuesta completa:" -ForegroundColor Red
        $_.Exception.Response
        
        # Mostrar los detalles del error si están disponibles
        if ($_.ErrorDetails.Message) {
            try {
                $errorContent = $_.ErrorDetails.Message | ConvertFrom-Json
                Write-Host "Detalles del error:" -ForegroundColor Red
                $errorContent
            }
            catch {
                Write-Host "No se pudo parsear el mensaje de error: $_" -ForegroundColor Red
            }
        }
    }
    
    Write-Host "`n3. Probando renovación de token..." -ForegroundColor Cyan
    $refreshToken = $loginResponse.refresh_token
    Write-Host "Refresh Token (primeros 20 caracteres): $($refreshToken.Substring(0, 20))..." -ForegroundColor Yellow
    
    $refreshHeaders = @{
        "Authorization" = "Bearer $refreshToken"
    }
    
    try {
        $refreshResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/refresh" -Method Post -Headers $refreshHeaders
        Write-Host "Renovación de token exitosa!" -ForegroundColor Green
        Write-Host "Nuevo access token (primeros 20 caracteres): $($refreshResponse.access_token.Substring(0, 20))..." -ForegroundColor Green
    }
    catch {
        Write-Host "Error al renovar token: $_" -ForegroundColor Red
    }
}
catch {
    Write-Host "Error al iniciar sesión: $_" -ForegroundColor Red
}
