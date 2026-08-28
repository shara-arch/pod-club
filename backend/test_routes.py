import unittest
from copy import deepcopy
from unittest.mock import patch

from routes import app


def empty_data():
    return {
        'users': [], 'channels': [], 'messages': [], 'threads': [], 'reports': [],
        'bannedUsers': [], 'invites': [], 'podcasts': [], 'music': [], 'playlists': [],
    }


class PodClubApiTests(unittest.TestCase):
    def setUp(self):
        self.data = empty_data()
        self.client = app.test_client()
        self.load_patcher = patch('routes.load_db', side_effect=lambda: self.data)
        self.save_patcher = patch('routes.save_db', side_effect=lambda payload: deepcopy(payload))
        self.load_patcher.start()
        self.save_patcher.start()

    def tearDown(self):
        self.load_patcher.stop()
        self.save_patcher.stop()

    def test_owner_can_only_create_five_channels(self):
        for number in range(5):
            response = self.client.post('/api/channels', json={
                'name': f'Channel {number}', 'ownerId': 'elly', 'communityId': 'main',
            })
            self.assertEqual(response.status_code, 201)

        response = self.client.post('/api/channels', json={
            'name': 'Sixth channel', 'ownerId': 'elly', 'communityId': 'main',
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('maximum of 5', response.get_json()['error'])

    def test_private_channel_requires_invite_to_join(self):
        self.data['channels'].append({'id': 'private-room', 'name': 'Private', 'isPrivate': True, 'members': ['owner']})
        denied = self.client.post('/api/channels/private-room/join', json={'userId': 'member'})
        self.assertEqual(denied.status_code, 403)

        self.data['invites'].append({'id': 'invite-1', 'code': 'join-1', 'channelId': 'private-room'})
        accepted = self.client.post('/api/channels/private-room/join', json={'userId': 'member', 'inviteCode': 'join-1'})
        self.assertEqual(accepted.status_code, 200)
        self.assertIn('member', accepted.get_json()['members'])

    def test_first_reply_creates_thread_and_updates_count(self):
        self.data['messages'].append({'id': 'message-1', 'channelId': 'room-1', 'author': {'name': 'Elly'}, 'content': 'Hello', 'replyCount': 0})
        thread = self.client.get('/api/threads/message-1')
        self.assertEqual(thread.status_code, 200)
        self.assertEqual(thread.get_json()['replies'], [])

        updated = self.client.patch('/api/threads/message-1', json={'replies': [{'id': 'reply-1', 'content': 'Hi'}]})
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(self.data['messages'][0]['replyCount'], 1)

    def test_ban_and_unban_user(self):
        banned = self.client.post('/api/banned-users', json={'username': 'abusive-user'})
        self.assertEqual(banned.status_code, 200)
        self.assertIn('abusive-user', self.data['bannedUsers'])

        unbanned = self.client.delete('/api/banned-users/abusive-user')
        self.assertEqual(unbanned.status_code, 204)
        self.assertNotIn('abusive-user', self.data['bannedUsers'])


if __name__ == '__main__':
    unittest.main()
