# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some Oxlint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and Oxlint's TypeScript related rules in your project.
# PodClub backend

Standalone Flask/PostgreSQL API for the PodClub frontend. It is intentionally kept outside the frontend project and has **not** been connected to it.

## Setup

1. Create a virtual environment and install dependencies:
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env`, then set `DATABASE_URL`.
    - Example Supabase connection (replace or use as-is):
       `postgresql://postgres:LPzrBJ-r-H54WSC@db.ygtyiwtpricqncwcigtb.supabase.co:5432/postgres`
    - You can copy the example with: `cp .env.example .env`
    - To apply migrations quickly: `bash scripts/setup_db.sh`
3. The initial migration is already committed. Apply it with:
   ```sh
   flask --app run.py db upgrade
   ```
4. Run locally with `flask --app run.py run --debug`.

To make a future schema change, run `flask --app run.py db migrate -m "describe change"`, review the generated revision, then run `flask --app run.py db upgrade`.

## API surface

- `GET|POST /api/channels`, `GET|PATCH|DELETE /api/channels/:id`
   - For development you can set a default user id so routes accept requests without the `X-User-ID` header:
      - Add `DEV_USER_ID=user1` to `.env` or set `DEV_USER_ID` in your environment.
      - The server will use `DEV_USER_ID` when running in `development` or when `TESTING` is enabled.
- `POST /api/channels/:id/invitations`, `POST /api/invitations/:token/join`
- `GET|POST /api/messages`, `PATCH|DELETE /api/messages/:id`
- `GET /api/threads/:rootId`, `POST /api/threads/:rootId/replies`
- `POST /api/reports`
- `GET /api/admin/channels`, `GET /api/admin/reports`
- `PATCH /api/admin/users/:id/ban`, `PATCH /api/admin/users/:id/unban`

Authentication is deliberately deferred. Until then, protected routes expect an `X-User-ID` header; replace this with JWT-derived identity when auth is implemented.

## Data rules

- Owners are limited to five channels.
- Private channels require an invitation/membership to join or post.
- Authors alone can edit or delete their messages.
- Admin-only moderation supports report review, banning, and unbanning.
