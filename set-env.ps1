# Script para configurar variables de entorno para la aplicación
$credentialsPath = Join-Path (Get-Location) "credentials\google-vision-key.json"
Write-Host "Configurando variable de entorno GOOGLE_APPLICATION_CREDENTIALS..."
$env:GOOGLE_APPLICATION_CREDENTIALS = $credentialsPath
Write-Host "Variable de entorno configurada: $env:GOOGLE_APPLICATION_CREDENTIALS"

# Verificar si el archivo existe
if (Test-Path $env:GOOGLE_APPLICATION_CREDENTIALS) {
    Write-Host "✅ Archivo de credenciales encontrado"
} else {
    Write-Host "❌ ADVERTENCIA: El archivo de credenciales no existe en la ruta especificada"
}

Write-Host ""
Write-Host "Para habilitar la API de Google Vision, sigue estos pasos:"
Write-Host "1. Accede a Google Cloud Console: https://console.cloud.google.com/"
Write-Host "2. Selecciona el proyecto 'proyecto-apuntes-ocr'"
Write-Host "3. Busca 'APIs y servicios' y selecciona 'Biblioteca de APIs'"
Write-Host "4. Busca 'Vision API' y habilítala"
Write-Host "5. Asegúrate de que la cuenta de servicio tenga el rol 'Cloud Vision API User'"
Write-Host ""
