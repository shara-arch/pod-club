# Frontend README – Music & Podcast Social Platform

## Overview

This is the frontend application for a **Music & Podcast Social Platform**, where users with shared interests in music and podcasts can create channels, chat, share images, invite others, and build communities.

The application is built using **React.js** with **Redux Toolkit** for state management. It is fully responsive and designed with a mobile-first approach.

> **Note:** This repository contains only the frontend implementation. The backend is developed separately using Flask and PostgreSQL.

---

# Tech Stack

* React.js
* Redux Toolkit
* React Router DOM
* Axios
* CSS / Tailwind CSS (or your preferred styling library)
* React Hook Form
* React Icons
* Jest
* React Testing Library

---

# Features

## Authentication

* User Registration
* User Login
* Logout
* Protected Routes
* Persistent Authentication

---

## User Features

### Channel Management

* Create a new group channel
* Maximum of 5 channels per user
* Edit channel description
* Delete channel

### Group Chat

* Send text messages
* Edit messages
* Delete messages
* Reply to messages
* Send image messages

### Invitations

* Generate invite links
* Share invite links
* Join multiple channels using invite links

### User Reporting

* Report abusive/offensive users

---

## Admin Features (Frontend)

* Login
* View all created channels
* View reported users
* Ban users
* Unban users

---

# Folder Structure

```
src/
│
├── app/
│   └── store.js
│
├── assets/
│
├── components/
│   ├── Navbar/
│   ├── Sidebar/
│   ├── Chat/
│   ├── Channel/
│   ├── Forms/
│   └── Shared/
│
├── features/
│   ├── auth/
│   ├── channels/
│   ├── messages/
│   ├── users/
│   └── reports/
│
├── hooks/
│
├── layouts/
│
├── pages/
│   ├── Login
│   ├── Register
│   ├── Dashboard
│   ├── Channel
│   ├── Profile
│   ├── Admin
│   └── NotFound
│
├── routes/
│
├── services/
│
├── utils/
│
├── App.jsx
├── main.jsx
└── index.css
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/yourusername/music-podcast-frontend.git
```

Navigate to the project

```bash
cd music-podcast-frontend
```

Install dependencies

```bash
npm install
```

Start the development server

```bash
npm run dev
```

The application will be available at

```
http://localhost:5173
```

---

# Available Scripts

Run development server

```bash
npm run dev
```

Build production version

```bash
npm run build
```

Preview production build

```bash
npm run preview
```

Run tests

```bash
npm test
```

---

# State Management

Redux Toolkit is used to manage the application state.

Main slices include:

* Authentication
* Users
* Channels
* Messages
* Reports
* Admin

---

# Routing

The application uses **React Router DOM**.

Example routes:

```
/
```

Home

```
/login
```

Login

```
/register
```

Register

```
/dashboard
```

Dashboard

```
/channel/:id
```

Group Chat

```
/admin
```

Admin Dashboard

---

# API Integration

The frontend communicates with the Flask backend using Axios.

Example API structure:

```
GET /api/channels

POST /api/login

POST /api/register

POST /api/messages

PUT /api/messages/:id

DELETE /api/messages/:id

POST /api/report

POST /api/invite
```

---

# Testing

Testing is implemented using:

* Jest
* React Testing Library

Example tests include:

* Authentication pages
* Protected routes
* Redux reducers
* Channel creation
* Message components
* Chat interface
* Admin dashboard

Run tests:

```bash
npm test
```

---

# Responsive Design

The application is designed using a mobile-first approach and supports:

* Mobile devices
* Tablets
* Laptops
* Desktop screens

---

# Future Improvements

* Real-time messaging with WebSockets
* Voice messages
* Audio sharing
* Music streaming previews
* Podcast episode sharing
* User profiles
* Emoji reactions
* Message search
* Notifications
* Dark mode
* Channel roles and permissions

---


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
