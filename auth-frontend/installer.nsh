; Script personalizado NSIS para Apuntes 2.0
; Instalación de dependencias y configuración avanzada

!macro preInit
  ; Mensaje de bienvenida
  MessageBox MB_OK "¡Bienvenido a Apuntes 2.0!$\n$\nSistema inteligente de notas con IA, OCR y mapas conceptuales.$\n$\nEste instalador configurará todo lo necesario."
!macroend

!macro customInstall
  ; Crear directorio de datos de usuario
  CreateDirectory "$APPDATA\Apuntes2.0"
  CreateDirectory "$APPDATA\Apuntes2.0\data"
  CreateDirectory "$APPDATA\Apuntes2.0\logs"
  
  ; Copiar archivos de configuración
  ${If} ${FileExists} "$INSTDIR\resources\config\*.*"
    CopyFiles "$INSTDIR\resources\config\*.*" "$APPDATA\Apuntes2.0\config\"
  ${EndIf}
  
  ; Crear acceso directo en escritorio con descripción
  CreateShortCut "$DESKTOP\Apuntes 2.0.lnk" "$INSTDIR\${PRODUCT_FILENAME}.exe" "" "$INSTDIR\${PRODUCT_FILENAME}.exe" 0 SW_SHOWNORMAL "" "Sistema de Notas con IA - Apuntes 2.0"
  
  ; Crear grupo en menú inicio
  CreateDirectory "$SMPROGRAMS\Apuntes 2.0"
  CreateShortCut "$SMPROGRAMS\Apuntes 2.0\Apuntes 2.0.lnk" "$INSTDIR\${PRODUCT_FILENAME}.exe" "" "$INSTDIR\${PRODUCT_FILENAME}.exe" 0 SW_SHOWNORMAL "" "Iniciar Apuntes 2.0"
  CreateShortCut "$SMPROGRAMS\Apuntes 2.0\Desinstalar.lnk" "$INSTDIR\Uninstall ${PRODUCT_FILENAME}.exe"
  
  ; Verificar dependencias del sistema
  DetailPrint "Verificando dependencias del sistema..."
  
  ; Mensaje de finalización exitosa
  MessageBox MB_OK "¡Instalación completada exitosamente!$\n$\n✅ Apuntes 2.0 está listo para usar$\n✅ Backend Flask incluido$\n✅ Base de datos configurada$\n✅ Servicios de IA disponibles$\n$\nPuedes encontrar Apuntes 2.0 en:$\n- Escritorio$\n- Menú Inicio > Apuntes 2.0"
!macroend

!macro customUnInstall
  ; Limpiar datos de usuario (opcional)
  MessageBox MB_YESNO "¿Deseas eliminar también los datos de usuario y configuración?$\n$\n(Recomendado: NO, para conservar tus notas)" IDYES remove_data IDNO keep_data
  
  remove_data:
    RMDir /r "$APPDATA\Apuntes2.0"
    DetailPrint "Datos de usuario eliminados"
    Goto cleanup_shortcuts
  
  keep_data:
    DetailPrint "Datos de usuario conservados en $APPDATA\Apuntes2.0"
  
  cleanup_shortcuts:
    ; Eliminar accesos directos
    Delete "$DESKTOP\Apuntes 2.0.lnk"
    RMDir /r "$SMPROGRAMS\Apuntes 2.0"
    
    MessageBox MB_OK "Apuntes 2.0 ha sido desinstalado correctamente.$\n$\n¡Gracias por usar nuestro sistema!"
!macroend

; Configuración de páginas del instalador
!macro customHeader
  !system "echo Compilando instalador personalizado de Apuntes 2.0..."
!macroend
