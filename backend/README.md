# PodClub Backend

This backend exposes the API used by the PodClub frontend and persists data in PostgreSQL. It does not use `db.json` for application data.

## Run locally

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
# Install PostgreSQL if it is not already installed, then start its service.
sudo apt-get install postgresql postgresql-client
sudo systemctl enable --now postgresql
# Create a database user and database once. Choose a secure password.
sudo -u postgres psql -c "CREATE USER podclub_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "CREATE DATABASE podclub OWNER podclub_user;"
# Configure the connection (see .env.example). A local .env file is loaded automatically.
export DATABASE_URL="postgresql://podclub_user:your_password@localhost:5432/podclub"
python app.py
```

The database-table definitions are also kept in `schema.sql` in this backend folder. The application creates the same tables automatically when it starts.

The server runs on:

- http://localhost:5000

## Health check

```bash
curl http://localhost:5000/api/health
```

## Tests

Run the backend Python Minitests:

```bash
cd backend
venv/bin/python -m unittest -v
```

Run the frontend Jest tests:

```bash
cd ../pod-club
npm test -- --runInBand
```

## Example API calls

```bash
curl "http://localhost:5000/api/channels?communityId=true-crime-circle"
curl http://localhost:5000/api/channels/general
curl -X POST http://localhost:5000/api/channels \
  -H "Content-Type: application/json" \
  -d '{"name":"Test channel","description":"API smoke test","communityId":"main","category":"General"}'
curl -X PATCH http://localhost:5000/api/channels/Test-channel \
  -H "Content-Type: application/json" \
  -d '{"description":"Updated description"}'
curl "http://localhost:5000/api/messages?channelId=general&_sort=timestamp&_order=asc"
curl -X POST http://localhost:5000/api/messages \
  -H "Content-Type: application/json" \
  -d '{"channelId":"general","author":{"id":"u1","name":"Tester","avatar":null},"content":"Hello from curl","timestamp":"2026-08-27T12:00:00Z","type":"text","replyCount":0}'
curl http://localhost:5000/api/threads/t1
curl -X POST http://localhost:5000/api/channels/general/join \
  -H "Content-Type: application/json" \
  -d '{"userId":"member-1","inviteId":"invite-id"}'
curl http://localhost:5000/api/admin/channels
curl -X POST http://localhost:5000/api/reports \
  -H "Content-Type: application/json" \
  -d '{"user":"member-1","reason":"Abusive content"}'
curl -X POST http://localhost:5000/api/banned-users \
  -H "Content-Type: application/json" \
  -d '{"username":"member-1"}'
curl -X POST http://localhost:5000/api/invites \
  -H "Content-Type: application/json" \
  -d '{"channelId":"general"}'
```

## Notes

- PATCH requests apply only the fields included in the request body.
- Data is stored in PostgreSQL. On first run, the backend creates `users`, `channels`, `messages`, `podcasts`, `music`, `artists`, `playlists`, and related tables, then inserts demo records.
- Set `DATABASE_URL` before starting the backend. Its local default is `postgresql://localhost/podclub`.
- `POST /api/invites` returns a `joinUrl`, such as `http://localhost:5174/channels?invite=general&inviteCode=join-...`.
- The Vite dev server in the frontend is configured to proxy `/api` traffic to this backend on port 5000.
