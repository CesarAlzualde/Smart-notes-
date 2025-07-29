import forms from '@tailwindcss/forms';
import typography from '@tailwindcss/typography';

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx,css}",
  ],
  safelist: [
    // Asegurar que estas clases problemáticas estén siempre disponibles
    'border-gray-300',
    'bg-gray-100',
    'text-gray-500',
    'hover:bg-gray-200',
    'focus:ring-2',
    'focus:ring-blue-500',
    'rounded-md',
    'shadow-sm'
  ],
  theme: {
    extend: {
      colors: {
        // Agregar colores básicos que faltan en v4
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
          950: '#030712',
        },
        primary: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
          950: '#1e1b4b',
        },
        secondary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#b9e6fe',
          300: '#7cd4fd',
          400: '#36bffa',
          500: '#0ca5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49',
        },
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
        'serif': ['Georgia', 'serif'],
        'mono': ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [
    // Ensure forms plugin is compatible with v4
    forms,
    typography,
  ],
};
