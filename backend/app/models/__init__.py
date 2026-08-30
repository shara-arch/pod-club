"""Model package.

Importing this module registers every mapped class on ``Base.metadata``, which
is what Alembic autogenerate compares against the live database. Anything not
imported here is invisible to migrations.
"""

from app.models.channel import Channel, ChannelMember, ChannelRole
from app.models.community import Community
from app.models.invite import Invite
from app.models.message import Message, MessageType, Thread, ThreadMessage
from app.models.report import Report, ReportStatus
from app.models.user import User

__all__ = [
    "Channel",
    "ChannelMember",
    "ChannelRole",
    "Community",
    "Invite",
    "Message",
    "MessageType",
    "Report",
    "ReportStatus",
    "Thread",
    "ThreadMessage",
    "User",
]
