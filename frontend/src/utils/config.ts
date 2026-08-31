/**
 * Utility functions for resolving and formatting backend and WebSocket URLs
 * for local development and Vercel/Render production environments.
 */

/**
 * Returns the normalized backend HTTP/HTTPS base URL.
 * Prefers process.env.NEXT_PUBLIC_BACKEND_URL, falling back to localhost.
 */
export function getBackendUrl(): string {
  const envBackendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
  if (envBackendUrl && envBackendUrl.trim() !== '') {
    return envBackendUrl.trim().replace(/\/+$/, '');
  }
  return 'http://localhost:8000';
}

/**
 * Returns the normalized WebSocket WSS/WS URL.
 * Guarantees forcing `wss://` in production / HTTPS environments to prevent mixed content errors.
 *
 * @param customWsUrl Optional explicit WebSocket URL to format
 */
export function getWebSocketUrl(customWsUrl?: string): string {
  let targetUrl = customWsUrl || process.env.NEXT_PUBLIC_WS_URL;

  // If no explicit WS URL provided, derive dynamically from BACKEND_URL
  if (!targetUrl || targetUrl.trim() === '') {
    const backendUrl = getBackendUrl();
    targetUrl = `${backendUrl}/ws/metrics`;
  }

  targetUrl = targetUrl.trim();

  // Step 1: Replace http:// or https:// with ws:// or wss:// if passed improperly
  if (targetUrl.startsWith('https://')) {
    targetUrl = targetUrl.replace(/^https:\/\//i, 'wss://');
  } else if (targetUrl.startsWith('http://')) {
    targetUrl = targetUrl.replace(/^http:\/\//i, 'ws://');
  }

  // Step 2: Ensure protocol scheme is present
  if (!targetUrl.startsWith('ws://') && !targetUrl.startsWith('wss://')) {
    targetUrl = `ws://${targetUrl}`;
  }

  // Step 3: Force wss:// in production or when running under HTTPS
  const isHttpsClient = typeof window !== 'undefined' && window.location.protocol === 'https:';
  const isProductionTarget =
    targetUrl.includes('onrender.com') ||
    targetUrl.includes('vercel.app') ||
    (!targetUrl.includes('localhost') && !targetUrl.includes('127.0.0.1'));

  if ((isHttpsClient || isProductionTarget) && targetUrl.startsWith('ws://')) {
    targetUrl = targetUrl.replace(/^ws:\/\//i, 'wss://');
  }

  return targetUrl;
}
