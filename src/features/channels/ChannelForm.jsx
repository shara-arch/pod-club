import React, { useState } from 'react';
import './channels.css';

const CATEGORIES = ['True Crime', 'Comedy', 'Music Lab', 'Tech & Dev', 'Culture', 'Sports Room'];


export default function ChannelForm({ initialValues, submitLabel = 'Create Channel', onSubmit, onCancel }) {
  const [name, setName] = useState(initialValues?.name || '');
  const [description, setDescription] = useState(initialValues?.description || '');
  const [isPrivate, setIsPrivate] = useState(initialValues?.isPrivate ?? true);
  const [category, setCategory] = useState(initialValues?.category || CATEGORIES[0]);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!name.trim()) {
      setError('Channel name is required.');
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      await onSubmit({ name: name.trim(), description: description.trim(), isPrivate, category });
    } catch (err) {
      setError(err.message || 'Something went wrong. Try again.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="pc-form" onSubmit={handleSubmit}>
      <div>
        <label className="pc-form__label" htmlFor="pc-channel-name">
          Channel Name
        </label>
        <input
          id="pc-channel-name"
          className="pc-form__input"
          placeholder="e.g. cold-case-debates"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </div>

      <div>
        <label className="pc-form__label" htmlFor="pc-channel-description">
          Description
        </label>
        <textarea
          id="pc-channel-description"
          className="pc-form__textarea"
          placeholder="What is this channel for? Theories, shared links, audio-space logs…"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>

      <div className="pc-form__row">
        <div className="pc-form__row-text">
          <strong>Private Channel</strong>
          <span>Only invited members can view and join</span>
        </div>
        <button
          type="button"
          className={`pc-toggle ${isPrivate ? 'pc-toggle--on' : ''}`}
          aria-pressed={isPrivate}
          onClick={() => setIsPrivate((v) => !v)}
        >
          <span className="pc-toggle__knob" />
        </button>
      </div>

      <div>
        <label className="pc-form__label" htmlFor="pc-channel-category">
          Category
        </label>
        <select
          id="pc-channel-category"
          className="pc-form__select"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>

      {error && <p className="pc-form__error">{error}</p>}

      <button className="pc-form__submit" type="submit" disabled={submitting}>
        {submitting ? 'Saving…' : submitLabel}
      </button>
      {onCancel && (
        <button className="pc-form__cancel" type="button" onClick={onCancel}>
          Cancel
        </button>
      )}
    </form>
  );
}
