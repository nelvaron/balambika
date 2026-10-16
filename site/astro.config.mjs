// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// The site is published as a GitHub Pages project site.
export const SITE = 'https://nelvaron.github.io';
export const BASE = '/balambika';

export default defineConfig({
  site: SITE,
  base: BASE,
  trailingSlash: 'always',
  build: {
    format: 'directory',
    // Keep CSS in files so the CSP never needs 'unsafe-inline' for <style>.
    inlineStylesheets: 'never',
  },
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'bg'],
    routing: { prefixDefaultLocale: false },
  },
  prefetch: { prefetchAll: true, defaultStrategy: 'hover' },
  // Never inline assets as data: URIs; the CSP allows fonts from 'self' only.
  vite: { build: { assetsInlineLimit: 0 } },
  markdown: { syntaxHighlight: false },
  integrations: [
    sitemap({
      i18n: { defaultLocale: 'en', locales: { en: 'en', bg: 'bg' } },
      filter: (page) => !page.includes('/404'),
    }),
  ],
  security: {
    // Astro hashes every script and stylesheet it emits and writes the
    // policy into a <meta http-equiv="content-security-policy"> tag.
    // GitHub Pages cannot send response headers, so frame-ancestors,
    // report-to and sandbox are not available here.
    csp: {
      algorithm: 'SHA-256',
      directives: [
        "default-src 'self'",
        "img-src 'self' data:",
        "font-src 'self'",
        "connect-src 'self'",
        "manifest-src 'self'",
        "object-src 'none'",
        "base-uri 'self'",
        "form-action 'none'",
        "upgrade-insecure-requests",
      ],
      styleDirective: {
        resources: ["'self'", { resource: "'unsafe-inline'", kind: 'attribute' }],
      },
      scriptDirective: { resources: ["'self'"] },
    },
  },
});
