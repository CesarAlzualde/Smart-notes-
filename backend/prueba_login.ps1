# Script simplificado para probar la autenticación
Write-Host "===== PRUEBA DE AUTENTICACION =====" -ForegroundColor Cyan

# Datos de login
$loginData = @{
    email = "test@example.com"
    password = "password123"
} | ConvertTo-Json

Write-Host "1. Intentando login..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" -Method Post -Body $loginData -ContentType "application/json" -ErrorAction Stop
    
    if ($response.access_token) {
        Write-Host "Login exitoso!" -ForegroundColor Green
        $token = $response.access_token
        
        # Guardar token en archivo para referencia
        $token | Out-File -FilePath "token.txt" -Encoding utf8
        Write-Host "Token guardado en token.txt" -ForegroundColor Cyan
        
        Write-Host "`n2. Probando acceso a endpoint protegido..." -ForegroundColor Yellow
        $headers = @{
            "Authorization" = "Bearer $token"
        }
        
        try {
            $profileResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/users/profile" -Method Get -Headers $headers -ErrorAction Stop
            Write-Host "Acceso exitoso al endpoint protegido!" -ForegroundColor Green
            $profileResponse | Format-List
        }
        catch {
            Write-Host "Error accediendo al endpoint protegido: $_" -ForegroundColor Red
            Write-Host $_.Exception.Response.StatusCode.value__
            
            if ($_.ErrorDetails) {
                Write-Host $_.ErrorDetails.Message -ForegroundColor Red
            }
        }
    }
    else {
        Write-Host "Error: La respuesta no contiene access_token" -ForegroundColor Red
    }
}
catch {
    Write-Host "Error en login: $_" -ForegroundColor Red
    
    if ($_.ErrorDetails) {
        Write-Host $_.ErrorDetails.Message -ForegroundColor Red
    }
}

Write-Host "`n===== FIN DE LA PRUEBA =====" -ForegroundColor Cyan
