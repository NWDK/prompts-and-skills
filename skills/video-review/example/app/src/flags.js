// Feature flags.
//
// Staging: values come from config/flags.staging.js, loaded by each page.
// Production: the deploy injects window.APP_FLAGS from the flag service.
// Production values are not stored in this repository: platform-lead@example.com holds them.

function flag(name) {
  return Boolean(window.APP_FLAGS && window.APP_FLAGS[name]);
}
