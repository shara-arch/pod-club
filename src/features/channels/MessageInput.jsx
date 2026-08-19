import React, { useState } from 'react';
import './channels.css';

// Props:
//   placeholder   - e.g. "Message #general…" or "Reply to thread…"
//   onSend(text)  - async function called with the trimmed text on send
export default function MessageInput({ placeholder = 'Message…', onSend }) {
  const [value, setValue] = useState('');
  const [sending, setSending] = useState(false);

  async function handleSend() {
    const trimmed = value.trim();
    if (!trimmed || sending) return;
    setSending(true);
    try {
      await onSend(trimmed);
      setValue('');
    } finally {
      setSending(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="pc-input-bar">
      <button className="pc-input-bar__plus" type="button" aria-label="Attach">
        +
      </button>
      <input
        className="pc-input-bar__field"
        placeholder={placeholder}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
      />
      <button
        className="pc-input-bar__send"
        type="button"
        aria-label="Send"
        disabled={!value.trim() || sending}
        onClick={handleSend}
      >
        ➤
      </button>
    </div>
  );
}
