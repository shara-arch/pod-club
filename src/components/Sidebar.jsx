import React from 'react'

export default function Sidebar({ channels = [] }) {
  return (
    <aside className="sidebar">
      <h3>Your Channels</h3>
      <ul>
        {channels.length > 0 ? (
          channels.map((c, i) => <li key={i}>{c}</li>)
        ) : (
          <li className="muted">No channels yet</li>
        )}
      </ul>
      <button className="btn primary">Create Channel</button>
    </aside>
  )
}
