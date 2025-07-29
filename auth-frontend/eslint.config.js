// eslint.config.js

// Import necessary plugins and utilities
import globals from "globals";
import pluginJs from "@eslint/js";
import tseslint from "typescript-eslint";
import pluginReact from "eslint-plugin-react";
import jsxA11y from "eslint-plugin-jsx-a11y";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";

export default [
  // Global ignores
  { ignores: ["dist/", "node_modules/"] },

  // Base configuration for all JS/TS files
  {
    files: ["**/*.{js,mjs,cjs,ts,jsx,tsx}"],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
  },

  // ESLint's recommended rules
  pluginJs.configs.recommended,

  // TypeScript ESLint's recommended rules
  ...tseslint.configs.recommended,

  // Configuration for React files (in src)
  {
    files: ["src/**/*.{ts,tsx}"],
    plugins: {
      react: pluginReact,
      "jsx-a11y": jsxA11y,
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
    },
    languageOptions: {
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
    },
    settings: {
      react: {
        version: "detect", // Automatically detect the React version
      },
    },
    rules: {
      // Apply recommended rules from plugins
      ...pluginReact.configs.recommended.rules,
      ...jsxA11y.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,

      // Custom rule adjustments
      "react-refresh/only-export-components": "warn",
      "react/react-in-jsx-scope": "off", // Not needed with modern React/Vite
      "react/no-inline-styles": "off", // Allow inline styles for CSS variables
      "react/prop-types": "off", // Not needed with TypeScript
    },
  },
];
