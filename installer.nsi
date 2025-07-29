; Apuntes 2.0 Installer Script
!define APPNAME "Apuntes 2.0"
!define COMPANYNAME "ApuntesAI"
!define DESCRIPTION "Sistema de gestión de notas con IA"
!define VERSIONMAJOR 2
!define VERSIONMINOR 0
!define VERSIONBUILD 0

; Configuración básica
Name "${APPNAME}"
Icon "assets\icon.ico"
OutFile "Apuntes2.0-Setup.exe"
InstallDir "$PROGRAMFILES64\${COMPANYNAME}\${APPNAME}"
RequestExecutionLevel admin

; Páginas del instalador
Page directory
Page components
Page instfiles

; Sección principal
Section "${APPNAME} (requerido)"
    SectionIn RO
    
    ; Crear directorio de instalación
    SetOutPath $INSTDIR
    
    ; Copiar archivos del backend
    File /r "backend\dist\ApuntesBackend\*"
    
    ; Copiar frontend construido
    CreateDirectory "$INSTDIR\frontend"
    File /r "auth-frontend\build\*" "$INSTDIR\frontend\"
    
    ; Crear launcher script
    FileOpen $4 "$INSTDIR\launch.bat" w
    FileWrite $4 "@echo off$\r$\n"
    FileWrite $4 "title ${APPNAME}$\r$\n"
    FileWrite $4 "cd /d $\"$INSTDIR$\"$\r$\n"
    FileWrite $4 "start /min ApuntesBackend.exe$\r$\n"
    FileWrite $4 "timeout /t 3 /nobreak >nul$\r$\n"
    FileWrite $4 "start http://localhost:5174$\r$\n"
    FileWrite $4 "echo ${APPNAME} iniciado. No cierres esta ventana.$\r$\n"
    FileWrite $4 "pause$\r$\n"
    FileWrite $4 "taskkill /im ApuntesBackend.exe /f >nul 2>&1$\r$\n"
    FileClose $4
    
    ; Crear acceso directo en escritorio
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\launch.bat" "" "$INSTDIR\icon.ico"
    
    ; Crear acceso directo en menú inicio
    CreateDirectory "$SMPROGRAMS\${COMPANYNAME}"
    CreateShortCut "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk" "$INSTDIR\launch.bat" "" "$INSTDIR\icon.ico"
    CreateShortCut "$SMPROGRAMS\${COMPANYNAME}\Desinstalar.lnk" "$INSTDIR\uninstall.exe"
    
    ; Crear desinstalador
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Registrar en Agregar/Quitar programas
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayIcon" "$\"$INSTDIR\icon.ico$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "NoRepair" 1
SectionEnd

; Sección de desinstalación
Section "Uninstall"
    ; Eliminar archivos
    Delete "$INSTDIR\*.*"
    RMDir /r "$INSTDIR"
    
    ; Eliminar accesos directos
    Delete "$DESKTOP\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${COMPANYNAME}\Desinstalar.lnk"
    RMDir "$SMPROGRAMS\${COMPANYNAME}"
    
    ; Eliminar registro
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}"
SectionEnd
