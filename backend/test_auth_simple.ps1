# Script simplificado para probar la autenticación
# 1. Login y captura de token
Write-Host "===== PRUEBA DE AUTENTICACIÓN SIMPLIFICADA =====" -ForegroundColor Cyan

try {
    # Paso 1: Login para obtener token
    Write-Host "1. Iniciando login..." -ForegroundColor Yellow
    
    $loginBody = @{
        email = "test@example.com"
        password = "password123"
    } | ConvertTo-Json
    
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json" -ErrorAction Stop
    
    if ($loginResponse.access_token) {
        # Guardar token en un archivo para poder verlo claramente
        $loginResponse.access_token | Out-File -FilePath "token_actual.txt" -Encoding utf8
        
        Write-Host "✅ Login exitoso!" -ForegroundColor Green
        Write-Host "Token guardado en 'token_actual.txt'" -ForegroundColor Green
        Write-Host "Primeros 30 caracteres del token: $($loginResponse.access_token.Substring(0, 30))..." -ForegroundColor Green
        
        # Paso 2: Usar el token para acceder a un endpoint protegido
        Write-Host "`n2. Accediendo a endpoint protegido..." -ForegroundColor Yellow
        
        $authHeaders = @{
            "Authorization" = "Bearer $($loginResponse.access_token)"
        }
        
        try {
            $profileResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/users/profile" -Method Get -Headers $authHeaders -ErrorAction Stop
            Write-Host "✅ Acceso exitoso al perfil!" -ForegroundColor Green
            Write-Host "Datos del perfil:" -ForegroundColor Cyan
            $profileResponse | ConvertTo-Json
        }
        catch {
            Write-Host "❌ Error al acceder al perfil:" -ForegroundColor Red
            Write-Host $_.Exception.Message -ForegroundColor Red
            if ($_.ErrorDetails) {
                Write-Host $_.ErrorDetails.Message -ForegroundColor Red
            }
        }
    }
    else {
        Write-Host "❌ Error: La respuesta no contiene un token de acceso!" -ForegroundColor Red
        Write-Host "Respuesta completa:" -ForegroundColor Yellow
        $loginResponse | ConvertTo-Json
    }
}
catch {
    Write-Host "❌ Error en el proceso de login:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($_.ErrorDetails) {
        Write-Host $_.ErrorDetails.Message -ForegroundColor Red
    }
}

Write-Host "`n===== FIN DE LA PRUEBA =====" -ForegroundColor Cyan
