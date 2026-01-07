import { Config } from "@jest/types";

const config: Config.InitialOptions = {
  testEnvironment: "jsdom",
  moduleFileExtensions: ["ts", "tsx", "js", "jsx", "svg"],
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
    "^src/(.*)$": "<rootDir>/src/$1",
    "^@components/(.*)$": "<rootDir>/src/components/$1",
    "^@styles/(.*)$": "<rootDir>/src/styles/$1",
    "\\.(scss|css)$": "jest-css-modules-transform",
    "^@layout/(.*)$": "<rootDir>/src/layout/$1",
    "\\.svg$": "<rootDir>/__mocks__/fileMock.js",
  },
  testMatch: ["<rootDir>/src/**/*.test.{ts,tsx,js,jsx}"],
  setupFilesAfterEnv: ["@testing-library/jest-dom/extend-expect"],
  transform: {
    "^.+\\.tsx?$": "ts-jest",
    // Keep Babel for plain JS if you need it:
    "^.+\\.jsx?$": "babel-jest",
  },
  transformIgnorePatterns: [
    // Ignore everything in node_modules except your @elilillyco/ux-lds-react package
    "node_modules/(?!(?:@elilillyco/ux-lds-react)/)",
  ],
};

export default config;
