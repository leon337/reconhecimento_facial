import { safeAppPath } from './app-navigation.js';

export function isOnboardingFormRoute(path) {
  return typeof path === 'string' && /^\/admin\/onboarding\/[a-f0-9]{32}$/i.test(path);
}

export function isAppFrameRoute(path) {
  return safeAppPath(path) && path !== '/admin/login' &&
    path !== '/admin/copilot' && path !== '/admin/copilot/embed/onboarding';
}

export function routeReached(expected, actual) {
  if (!isAppFrameRoute(actual) || !safeAppPath(expected)) return false;
  if (expected === actual) return true;
  return ['/admin/users/new','/admin/onboarding/new'].includes(expected) &&
    isOnboardingFormRoute(actual);
}

export function isTrustedAppMessage(event, frameWindow, origin) {
  return Boolean(frameWindow && event && event.origin === origin &&
    event.source === frameWindow && event.data && typeof event.data === 'object' &&
    !Array.isArray(event.data));
}
