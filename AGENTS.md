# Syncademic v2

This branch is a from-scratch rewrite of Syncademic. It shares no history with
`main`, which holds the current production app (Flutter, Firebase Functions,
GPT-generated customization rules). Use `main` as a reference for product
behavior and domain concepts, not for code.

Syncademic syncs university schedules (ICS feeds) into Google Calendar and
cleans them up along the way: readable titles, one color per course,
irrelevant events removed.

## Direction

- **Modern stack.** Rewrite the product with today's technologies, especially
  the frontend, the AI layer, and the synchronization engine.
- **Agents, not one-shot prompts.** Customization is built by a modern agent
  that the user can talk to, correct, and iterate with. Customizations should
  be personal and easy to refine over time, not generated once and frozen.
- **Code instead of rules.** Instead of the rigid JSON rule format used on
  `main`, the AI probably writes small Python programs that transform events on
  each sync. These run in [Monty](https://github.com/pydantic/monty), a
  minimal, secure Python interpreter written in Rust for use by AI, so
  AI-written code stays sandboxed.
- **Cloudflare.** Move the website, and probably the rest of the
  infrastructure, to Cloudflare. Stay on the free tier where possible.

## Status

Nothing is implemented yet. Stack choices beyond the points above are open;
confirm them with the owner before committing to one.
