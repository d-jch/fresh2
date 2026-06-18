---
description: |
  This chapter goes over some fundamental concepts of Fresh.
---

The way Fresh works is that it receives a
[`Request`](https://developer.mozilla.org/en-US/docs/Web/API/Request), passes it
through one or more middlewares until one of them responds. This can be an HTML
response, a JSON response or any other response for that matter.

If the response was HTML and contained Islands (=interactive Preact components),
Fresh will boot them up in the browser and execute the relevant JavaScript.

Here is an overview of the basic concepts in Fresh:

- [**Architecture**](architecture.md) - How requests flow through
  Fresh, from middleware to islands
- [**App**](app.md) - Holds all the information about your app, like
  routes, etc
- [**Middleware**](middleware.md) - Respond to a request and return
  a `Response`. Used to set headers, or pass state to other middlewares. When a
  middleware doesn't call the next one and returns a response, it's usually
  called a "handler".
- [**Context**](context.md) - Passed through every middleware. Use
  this to share state, trigger redirects or render HTML.
- [**Routing**](routing.md) - Responds to a particular URL and runs
  as chain of middlewares if it matches
- [**Data Fetching**](data-fetching.md) - Load data on the server
  and pass it to page components
- [**Islands**](islands.md) - Render interactive Preact components
  on the client
- [**Signals**](signals.md) - Reactive state management for islands
- [**Static Files**](static-files.md) - Serve images, CSS, and other
  assets
- [**File Routing**](file-routing.md) - Convention-based routing
  from the filesystem

Advanced concepts:

- [**App wrapper**](../advanced/app-wrapper.md) - Responsible for the outer HTML
  structure, usually up to the `<body>`-tag
- [**Layouts**](../advanced/layouts.md) - Re-use a shared layout when calling
  `ctx.render()` across routes
- [**Partials**](../advanced/partials.md) - Stream in server generated content
  on the current page
