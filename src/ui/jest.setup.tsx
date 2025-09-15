import crypto from "crypto";
import { TextEncoder } from 'util';

global.TextEncoder = TextEncoder;

Object.defineProperty(globalThis, 'crypto', {
  value: {
    getRandomValues: arr => crypto.randomBytes(arr.length)
  }
});

jest.mock('react-chartjs-2', () => ({
  Doughnut: () => null
}));
