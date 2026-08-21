import React, { useRef, useState } from 'react';
import './channels.css';


export default function MessageInput({ placeholder = 'Message…', onSend, onSendImage }) {
  const [value, setValue] = useState('');
  const [sending, setSending] = useState(false);
  const fileInput = useRef(null);

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
  function handleImage(event) {
    const file = event.target.files?.[0];
    if (!file || !onSendImage) return;
    const reader = new FileReader();
    reader.onload = async () => { await onSendImage(reader.result, file.name); };
    reader.readAsDataURL(file);
    event.target.value = '';
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="pc-input-bar">
      <input ref={fileInput} onChange={handleImage} type="file" accept="image/*" className="hidden" />
      <button className="pc-input-bar__plus" type="button" aria-label="Attach image" onClick={() => fileInput.current?.click()}>
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
