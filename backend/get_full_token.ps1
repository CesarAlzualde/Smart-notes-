$loginData = @{
    email = "test@example.com"
    password = "password123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" -Method Post -Body $loginData -ContentType "application/json"

# Guardar el token completo en una variable y mostrarlo completo
$fullToken = $response.access_token
Write-Host "Token completo:" -ForegroundColor Green
Write-Host $fullToken

# Guardar en un archivo para referencia
$fullToken | Out-File -FilePath "current_token.txt"
Write-Host "Token guardado en current_token.txt" -ForegroundColor Green

# Probar un endpoint con el token completo
$headers = @{
    "Authorization" = "Bearer $fullToken"
}

Write-Host "`nProbando acceso a endpoint protegido..." -ForegroundColor Yellow
try {
    $profileResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/users/profile" -Method Get -Headers $headers
    Write-Host "Acceso exitoso a /api/users/profile" -ForegroundColor Green
    $profileResponse
} catch {
    Write-Host "Error al acceder: $_" -ForegroundColor Red
}
