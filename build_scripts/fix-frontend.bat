@echo off
echo ===== REPARANDO DEPENDENCIAS DEL FRONTEND =====
echo.

cd auth-frontend

echo [1/4] Limpiando cache de npm...
call npm cache clean --force

echo [2/4] Instalando dependencia browserslist actualizada...
call npm install browserslist@latest --save-dev

echo [3/4] Desactivando plugin PWA que causa conflictos...
cd ..

echo [4/4] Reparando configuracion de Vite...
echo // vite.config.ts actualizado > auth-frontend\vite.config.ts.new
echo import { defineConfig } from 'vite'; >> auth-frontend\vite.config.ts.new
echo import react from '@vitejs/plugin-react'; >> auth-frontend\vite.config.ts.new
echo. >> auth-frontend\vite.config.ts.new
echo export default defineConfig({ >> auth-frontend\vite.config.ts.new
echo   plugins: [react()], >> auth-frontend\vite.config.ts.new
echo   build: { >> auth-frontend\vite.config.ts.new
echo     outDir: 'dist', >> auth-frontend\vite.config.ts.new
echo     emptyOutDir: true, >> auth-frontend\vite.config.ts.new
echo   }, >> auth-frontend\vite.config.ts.new
echo }); >> auth-frontend\vite.config.ts.new

move /Y auth-frontend\vite.config.ts.new auth-frontend\vite.config.ts

echo.
echo ===== REPARACION COMPLETADA =====
echo Ahora intenta ejecutar el empaquetado nuevamente
echo.
pause
