---
description: "Extend fresh with plugins"
---

Fresh itself can be extended through the methods available on the
[`App`](../concepts/app.md) class or on the `Builder` class. Most of the
features in Fresh itself are built using these APIs.

## Custom middlewares

If you need to modify requests, add HTTP headers or pass additional data to
other [middlewares](../concepts/middleware.md) via `ctx.state`, then going with
a middleware is the way to go.

```ts middleware/fresh.ts
const addXFreshHeader = define.middleware(async (ctx) => {
  const res = await ctx.next();
  res.headers.set("X-Fresh", "served by Fresh");
  return res;
});
```

Learn more about [middlewares](../concepts/middleware.md).

## Creating reusable plugins

Since Fresh plugins are just middlewares and route handlers, creating a reusable
plugin is as simple as exporting a function that returns a middleware:

```ts plugins/request-id.ts
import type { MiddlewareFn } from "fresh";

export function requestId(): MiddlewareFn<{ requestId: string }> {
  return async (ctx) => {
    ctx.state.requestId = crypto.randomUUID();
    const res = await ctx.next();
    res.headers.set("X-Request-Id", ctx.state.requestId);
    return res;
  };
}
```

```ts main.ts
import { App, staticFiles } from "fresh";
import { requestId } from "./plugins/request-id.ts";

const app = new App()
  .use(staticFiles())
  .use(requestId())
  .fsRoutes();
```

For more complex plugins, you can combine multiple middlewares, add routes, or
use the [`Builder`](../advanced/builder.md) hooks for build-time processing.

## Built-in plugins

Fresh ships with the following plugins:

- [cors()](cors.md) - Set CORS HTTP headers
- [csrf()](csrf.md) - CSRF protection
- [csp()](csp.md) - Content Security Policy headers
- [trailingSlashes()](trailing-slashes.md) - Enforce trailing slash
  behavior
