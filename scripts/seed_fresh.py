

from datetime import datetime, timezone
from app import create_app
from app.extensions import db
from app.models import User, Channel, ChannelMembership, Message


def now_utc():
    return datetime.now(timezone.utc)


def seed():
    app = create_app()
    with app.app_context():
        print("🌱 Seeding fresh database...")
        
        # 1. Create users
        users = [
            User(
                id="admin",
                email="admin@podclub.com",
                display_name="Admin User",
                role="admin",
                created_at=now_utc()
            ),
            User(
                id="user1",
                email="alice@podclub.com",
                display_name="Alice",
                role="user",
                created_at=now_utc()
            ),
            User(
                id="user2",
                email="bob@podclub.com",
                display_name="Bob",
                role="user",
                created_at=now_utc()
            ),
            User(
                id="user3",
                email="charlie@podclub.com",
                display_name="Charlie",
                role="user",
                created_at=now_utc()
            ),
        ]
        
        for user in users:
            user.set_password("password123")
            db.session.add(user)
        db.session.commit()
        print(f"✅ Created {len(users)} users")
        
        # 2. Create channels
        channels = [
            Channel(
                id="general",
                name="General",
                description="Main discussion for the community",
                category="True Crime",
                is_private=False,
                owner_id="user1",
                created_at=now_utc()
            ),
            Channel(
                id="weekly-recommendations",
                name="Weekly Recommendations",
                description="Share podcast episodes worth a listen",
                category="True Crime",
                is_private=False,
                owner_id="user1",
                created_at=now_utc()
            ),
            Channel(
                id="case-file-theories",
                name="Case File Theories",
                description="Break down evidence and swap theories",
                category="True Crime",
                is_private=False,
                owner_id="user2",
                created_at=now_utc()
            ),
        ]
        
        for channel in channels:
            db.session.add(channel)
        db.session.commit()
        print(f"✅ Created {len(channels)} channels")
        
        # 3. Add members to channels
        memberships = [
            ChannelMembership(channel_id="general", user_id="user1"),
            ChannelMembership(channel_id="general", user_id="user2"),
            ChannelMembership(channel_id="general", user_id="user3"),
            ChannelMembership(channel_id="weekly-recommendations", user_id="user1"),
            ChannelMembership(channel_id="weekly-recommendations", user_id="user2"),
            ChannelMembership(channel_id="case-file-theories", user_id="user2"),
            ChannelMembership(channel_id="case-file-theories", user_id="user3"),
        ]
        
        for membership in memberships:
            db.session.add(membership)
        db.session.commit()
        print(f"✅ Added {len(memberships)} channel memberships")
        
        # 4. Add some messages
        messages = [
            Message(
                id="m1",
                channel_id="general",
                author_id="user1",
                content="Have you guys checked the neighborhood layout map yet? It changes everything.",
                message_type="text",
                created_at=now_utc()
            ),
            Message(
                id="m2",
                channel_id="general",
                author_id="user2",
                content="Ep 42: The Midnight Alibi - The Serial Killer Next Door",
                message_type="episode-share",
                subtitle="The Serial Killer Next Door",
                created_at=now_utc()
            ),
            Message(
                id="m3",
                channel_id="general",
                author_id="user3",
                content="I found a new podcast called 'Dark Audio Archives' - highly recommend!",
                message_type="text",
                created_at=now_utc()
            ),
        ]
        
        for message in messages:
            db.session.add(message)
        db.session.commit()
        print(f"✅ Created {len(messages)} messages")
        
        print("\n🎉 Database seeded successfully!")
        print("\nCredentials:")
        print("  Admin: admin@podclub.com / password123")
        print("  User:  alice@podclub.com / password123")
        print("  User:  bob@podclub.com / password123")


if __name__ == "__main__":
    seed()