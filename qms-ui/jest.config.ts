import { Config } from '@jest/types';

const config: Config.InitialOptions = {
  testEnvironment: "jsdom",
  moduleFileExtensions: ["ts", "tsx", "js","jsx"],
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
    '\\.(scss|css)$': 'jest-css-modules-transform',
  },
  testMatch: ["<rootDir>/src/**/*.test.{ts,tsx,js,jsx}"],
  setupFilesAfterEnv: ["@testing-library/jest-dom/extend-expect", "./jest.setup.tsx"],
  transform: {
    '^.+\\.jsx?$':'babel-jest',
    '^.+\\.tsx?$':'babel-jest',
    '^.+\\.svg$': './svgTransform.ts',
  },
  transformIgnorePatterns: [
    'node_modules/(?!(@elilillyco/ux-lds-react|@azure/msal-react)/)',
  ],
};

export default config;
