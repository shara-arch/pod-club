#!/usr/bin/env python3
"""Seed the database with a few dummy users for manual testing.

Usage:
  python scripts/seed_dummy_users.py

This script requires the app's `DATABASE_URL` to be configured (see .env).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import User, Role


def seed():
    app = create_app()
    with app.app_context():
        users = [
            User(id="admin", email="admin@example.com", display_name="Admin User", role=Role.ADMIN),
            User(id="user1", email="alice@example.com", display_name="Alice"),
            User(id="user2", email="bob@example.com", display_name="Bob"),
            User(id="banned", email="banned@example.com", display_name="Banned User", is_banned=True),
        ]

        for u in users:
            existing = db.session.get(User, u.id)
            if existing:
                existing.email = u.email
                existing.display_name = u.display_name
                existing.role = u.role
                existing.is_banned = u.is_banned
            else:
                db.session.add(u)

        db.session.commit()
        print("Seeded users: admin, user1, user2, banned")


if __name__ == "__main__":
    seed()
