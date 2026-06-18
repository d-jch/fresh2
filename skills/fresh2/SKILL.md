---
name: fresh2
description: |
  Fresh 2 framework reference with complete API documentation, code examples, and migration guide from Fresh 1. Use this skill when working with Fresh framework, Deno web development, island architecture, Preact SSR, routing, file routing, middleware, islands, signals, island props serialization, forms, layouts, static files, Vite integration, deployment, testing, data fetching, error handling, partials, WebSockets, plugins, migration, or any Fresh-related code. Provides accurate Fresh 2 APIs: define.handlers, define.page, page() helper, HttpError, @preact/signals, @fresh/plugin-vite, _layout.tsx, _error.tsx, _app.tsx, vite.config.ts. Includes complete documentation in references/ directory.
---

# Fresh 2 Framework Reference

Fresh 2 is a full-stack web framework for Deno with Island Architecture. This skill prevents using outdated Fresh 1 patterns.

## Quick Identification

| Pattern | Version |
|---------|---------|
| `import { App } from "fresh"` | Fresh 2 ✓ |
| `import { start } from "$fresh/server.ts"` | Fresh 1 ✗ |
| `vite.config.ts` with `@fresh/plugin-vite` | Fresh 2 ✓ |
| `fresh.config.ts` or `fresh.gen.ts` | Fresh 1 ✗ |

## Key API Changes (Fresh 1 → Fresh 2)

| Feature | Fresh 1 (outdated) | Fresh 2 (correct) |
|---------|-------------------|-------------------|
| Handler signature | `GET(req, ctx)` | `GET(ctx)` |
| Middleware | `(req, ctx) =>` | `(ctx) =>` |
| Pass data to page | `ctx.render({ data })` | `page({ data })` |
| 404 handling | `ctx.renderNotFound()` | `throw new HttpError(404)` |
| Imports | `"$fresh/server.ts"` | `"fresh"` |
| Config | `fresh.config.ts` | `vite.config.ts` |
| Manifest | `fresh.gen.ts` | (removed) |
| Dev server | `dev.ts` | `vite` |
| Error pages | `_404.tsx` + `_500.tsx` | `_error.tsx` |

For file routes that load data in `define.handlers()`, return `page({ data })`
and read `props.data` in `define.page<typeof handler>()`. `ctx.render(<JSX />)`
is valid in programmatic routes such as `app.get()`, but do not use the Fresh 1
`ctx.render({ data })` pattern for handler-to-page data.

Fresh 2 supports both file-based `routes/_error.tsx` error pages and
programmatic `app.onError()` / `app.notFound()` handlers. Do not claim
`_error.tsx` is unsupported.

## Essential Code Patterns

```ts
// main.ts
import { App, staticFiles } from "fresh";
export const app = new App().use(staticFiles()).fsRoutes();

// Handler with page()
import { page, HttpError } from "fresh";
export const handler = define.handlers({
  async GET(ctx) {
    const item = await db.find(ctx.params.id);
    if (!item) throw new HttpError(404);
    return page({ item });
  },
});

// Page component
export default define.page<typeof handler>(({ data }) => {
  return <h1>{data.item.name}</h1>;
});

// Island
import { useSignal } from "@preact/signals";
export default function Counter() {
  const count = useSignal(0);
  return <button onClick={() => count.value++}>{count}</button>;
}

// vite.config.ts
import { defineConfig } from "vite";
import { fresh } from "@fresh/plugin-vite";
export default defineConfig({ plugins: [fresh()] });

// client.ts (CSS imports)
import "./assets/styles.css";
```

## File Routing Quick Reference

| File | Route | Example |
|------|-------|---------|
| `index.ts` | `/` | `/` |
| `about.ts` | `/about` | `/about` |
| `[slug].ts` | `/:slug` | `/foo` |
| `[...path].ts` | `/:path*` | `/a/b/c` |
| `(group)/_layout.tsx` | (group layout) | shared UI |

## Partials And View Transitions Quick Reference

Use `f-client-nav` with `<Partial name="...">` for partial navigation. Use
`f-partial="/partials/..."` when a link, button, or form should fetch an
optimized partial response. For animated partial navigations, add
`f-view-transition` alongside `f-client-nav`; details are in
`references/advanced/view-transitions.md`.

## Island Props Serialization Quick Reference

Fresh can serialize more than plain JSON for island props. Supported values
include primitives, `bigint`, special numbers, arrays, plain objects, `Date`,
`URL`, `RegExp`, `Set`, `Map`, `Uint8Array`, `Signal`, computed signals,
Temporal values, JSX elements, and circular/shared references.

Do not pass functions, class instances, symbols, `WeakMap`, `WeakSet`, streams,
or promises as island props. For details, read
`references/advanced/serialization.md`.

## Documentation References

For detailed information, see `references/` directory:

| Category | File | Description |
|----------|------|-------------|
| **Getting Started** | `references/introduction/index.md` | Framework overview |
| | `references/getting-started/index.md` | Project setup |
| **Core Concepts** | `references/concepts/app.md` | App class |
| | `references/concepts/context.md` | Context object |
| | `references/concepts/routing.md` | Routing |
| | `references/concepts/file-routing.md` | File routing |
| | `references/concepts/middleware.md` | Middleware |
| | `references/concepts/islands.md` | Islands |
| | `references/concepts/signals.md` | Signals |
| | `references/concepts/data-fetching.md` | Data fetching |
| | `references/concepts/layouts.md` | Layouts |
| | `references/concepts/static-files.md` | Static files |
| | `references/concepts/architecture.md` | Architecture |
| **Advanced** | `references/advanced/forms.md` | Forms |
| | `references/advanced/vite.md` | Vite integration |
| | `references/advanced/define.md` | Define helpers |
| | `references/advanced/error-handling.md` | Error handling |
| | `references/advanced/serialization.md` | Serialization |
| | `references/advanced/view-transitions.md` | View transitions |
| | `references/advanced/websockets.md` | WebSockets |
| | `references/advanced/partials.md` | Partials |
| | `references/advanced/app-wrapper.md` | App wrapper |
| | `references/advanced/head.md` | Head management |
| | `references/advanced/layouts.md` | Programmatic layouts |
| | `references/advanced/api-reference.md` | API reference |
| | `references/advanced/builder.md` | Builder (legacy) |
| | `references/advanced/environment-variables.md` | Environment vars |
| | `references/advanced/opentelemetry.md` | OpenTelemetry |
| | `references/advanced/troubleshooting.md` | Troubleshooting |
| **Plugins** | `references/plugins/cors.md` | CORS |
| | `references/plugins/csrf.md` | CSRF |
| | `references/plugins/csp.md` | CSP |
| | `references/plugins/trailing-slashes.md` | Trailing slashes |
| | `references/plugins/ip-filter.md` | IP filter |
| **Deployment** | `references/deployment/deno-deploy.md` | Deno Deploy |
| | `references/deployment/docker.md` | Docker |
| | `references/deployment/cloudflare-workers.md` | Cloudflare Workers |
| | `references/deployment/deno-compile.md` | Deno Compile |
| **Testing** | `references/testing/index.md` | Testing |
| **Migration** | `references/migration-guide/index.md` | Migration guide |
| **Examples** | `references/examples/api-routes.md` | API routes |
| | `references/examples/common-patterns.md` | Common patterns |
| | `references/examples/session-management.md` | Sessions |
| | `references/examples/sharing-state-between-islands.md` | Shared state |
| | `references/examples/active-links.md` | Active links |
| | `references/examples/daisyui.md` | DaisyUI |
| | `references/examples/markdown.md` | Markdown |
| | `references/examples/rendering-raw-html.md` | Raw HTML |
| **Contributing** | `references/contributing/index.md` | Contributing |
| **Index** | `references/INDEX.md` | Full index |
| | `references/concepts/index.md` | Concepts index |
| | `references/advanced/index.md` | Advanced index |
| | `references/plugins/index.md` | Plugins index |
| | `references/deployment/index.md` | Deployment index |
| | `references/examples/index.md` | Examples index |

## Key Imports

```ts
import { App, staticFiles, page, HttpError } from "fresh";
import { createDefine } from "fresh";
import { useSignal, useComputed } from "@preact/signals";
import { IS_BROWSER } from "fresh/runtime";
```
