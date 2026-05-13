// Utility to check if real API e2e mode is enabled
export function isRealApiE2e() {
  return process.env.REAL_API_E2E === '1';
}
