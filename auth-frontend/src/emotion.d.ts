import '@emotion/react';
import { Theme as CustomTheme } from './theme/themeConstants';

declare module '@emotion/react' {
  export type Theme = CustomTheme;
}
