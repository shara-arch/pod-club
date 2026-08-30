# PodClub Backend — Phase 1

FastAPI + PostgreSQL API for PodClub, built as a folder inside the existing
frontend repo. This document covers what phase 1 does and does not include, and
how to run the database layer.

## Scope

Phase 1 is the backend only. It is **not** wired to the React frontend — the
frontend still runs against its `json-server` mock (`npm run api`), and no
frontend file is modified by this work. The API is exercised standalone through
Postman.

Deliberately out of scope for now: WebSockets (messaging uses polling instead),
OAuth or social login, and any role system beyond the `is_admin` flag.

## Work split

The backend is divided into four areas, one branch per person, merged into
`main` by pull request.

| Area | Branch | Contents |
|---|---|---|
| Database & Models | `feat/db-models` | Docker Compose Postgres, SQLAlchemy models, Alembic migrations |
| Core CRUD API | `feat/core-api` | FastAPI app and routers, Pydantic schemas, CRUD endpoints |
| Auth | `feat/auth` | Password hashing, login endpoint, JWT, `get_current_user` |
| Messaging + Testing/Docs | `feat/messaging-tests` | Polling message endpoints, tests, Postman collection |

**This branch is Area 1 only.** There is no `app/main.py` and no running API
yet — that arrives with Area 2. Compose therefore starts Postgres and nothing
else.

## Running the database

```bash
cd backend
cp .env.example .env          # never commit .env
docker compose up -d          # Postgres on localhost:5432
```

Then apply migrations from the host:

```bash
pip install -r requirements.txt
alembic upgrade head
```

Verify:

```bash
docker compose exec db psql -U podclub -d podclub -c '\dt'
```

Useful checks that need no database at all, since Alembic can render SQL
offline:

```bash
alembic upgrade head --sql        # inspect the DDL before running it
alembic downgrade head:base --sql # confirm the rollback path
```

To tear the database down completely, including its volume:

```bash
docker compose down -v
```

## Migrations

Alembic reads `DATABASE_URL` from the environment via `app/config.py`;
`alembic.ini` holds no credentials.

Creating a new migration after changing a model:

```bash
alembic revision --autogenerate -m "what changed"
```

Two rules that matter:

1. **Import new models in `app/models/__init__.py`.** Autogenerate compares the
   database against `Base.metadata`, and a model that is never imported is not
   in that metadata — it will silently produce an empty migration.
2. **Read the generated file before committing it.** Autogenerate does not
   detect table or column renames (it emits a drop plus an add, which loses
   data), and it does not drop Postgres ENUM types on downgrade — `0001` patches
   that by hand.

## Schema

Nine tables. Ids are strings: slugs for communities and channels, matching the
ids the frontend already uses (`true-crime-circle`, `case-file-theories`), and
UUIDs everywhere else.

| Table | Purpose |
|---|---|
| `communities` | Listening rooms that own channels |
| `users` | Accounts, plus `is_admin` and the `is_banned` / `banned_at` / `banned_by_id` moderation flags |
| `channels` | Channels within a community; unique on `(community_id, name)` |
| `channel_members` | Membership and `owner` / `member` role — the access check for private channels |
| `messages` | Channel messages: `text`, `image` or `episode-share`, with `reply_to_id` for direct replies |
| `threads` | A thread hanging off one root message, with a denormalised `reply_count` |
| `thread_messages` | Replies inside a thread |
| `invites` | Invite links carrying an unguessable token |
| `reports` | Moderation queue: who was reported, where, why, and its `open` / `reviewed` / `dismissed` status |

### Decisions worth knowing

**Passwords are not in this branch.** `users` has no `password_hash` column.
Hashing belongs to Area 3, which adds it in its own migration. Nothing here
authenticates anyone, so nothing here should be exposed to the internet yet.

**Edits and deletes are soft.** `messages` and `thread_messages` carry
`edited_at` and `deleted_at` rather than being removed, so the client can render
an "edited" marker and a deleted message does not orphan its replies.

**Invites use a token, not the channel id.** The frontend currently builds
`/channels?invite=<channelId>` from the slug, which anyone can guess. The
`invites` table stores a random token instead, with optional `expires_at`,
`max_uses` and `revoked_at`. Area 2 should accept the token, not the slug.

**Messages are indexed on `(channel_id, created_at)`.** That is exactly the
query the polling endpoint runs — "messages in this channel newer than X" — so
polling does not degrade as history grows.

**Timestamps are `TIMESTAMP WITH TIME ZONE`, defaulted by the database.** The
frontend sends ISO-8601 UTC (`2026-08-18T10:14:00Z`); storing naive local
timestamps would make ordering wrong for anyone outside the server's timezone.

**Constraint names come from a naming convention** set on the metadata in
`app/db.py`, so migrations are reproducible across environments instead of
depending on names the database happens to assign.

## Layout

```
backend/
├── app/
│   ├── config.py                     settings from environment / .env
│   ├── db.py                         engine, session factory, Base, get_db
│   └── models/                       SQLAlchemy models
│       ├── community.py
│       ├── user.py
│       ├── channel.py                Channel, ChannelMember
│       ├── message.py                Message, Thread, ThreadMessage
│       ├── invite.py
│       └── report.py
├── alembic/
│   ├── env.py
│   └── versions/0001_initial_schema.py
├── alembic.ini
├── docker-compose.yml                Postgres 16
├── requirements.txt
├── .env.example
└── README.md
```

Routers depend on `get_db` from `app/db.py` rather than importing `SessionLocal`
directly, so tests can override the dependency with a transactional session.
