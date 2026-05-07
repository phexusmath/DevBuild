/**
 * shim.js — injected into every game before any game code runs.
 *
 * primary job: make the game think it is running at the top level.
 * secondary job: patch other common breakage points.
 * 
 * optimized for performance: uses cached values instead of getters,
 * minimal DOM operations, and simplified URL checks.
 */
(function () {
  const win = window;

  // use getter descriptors, not value descriptors.
  // window.top/parent/frameElement/self are native accessor properties in browsers.
  // replacing them with value descriptors changes the descriptor type, forcing V8 to
  // restructure the window object's hidden class and de-optimizing everything that
  // touches it. keeping them as accessors (get:) avoids that entirely.
  try {
    Object.defineProperty(window, 'top',         { get: () => win,  configurable: true });
  } catch(e) {}
  try {
    Object.defineProperty(window, 'parent',      { get: () => win,  configurable: true });
  } catch(e) {}
  try {
    Object.defineProperty(window, 'self',        { get: () => win,  configurable: true });
  } catch(e) {}
  try {
    Object.defineProperty(window, 'frameElement',{ get: () => null, configurable: true });
  } catch(e) {}

  // silence document.domain assignments from games hosted on other domains
  /*try {
    Object.defineProperty(document, 'domain', {
      get() { return location.hostname; },
      set(v) {},
      configurable: true,
    });
  } catch(e) {}
*/
})();
