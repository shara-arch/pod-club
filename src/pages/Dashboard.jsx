import React from 'react'
import BottomNav from '../components/BottomNav'

export default function Dashboard() {
  const featured = {
    title: 'True Crime Circle',
    subtitle: 'Sifting through the evidence they left behind.',
    tag: 'TRUE CRIME',
    active: '4.2k active',
  }

  const trending = [
    { title: 'Deep Dive: The Somerton Case', listeners: '1.2k listening' },
    { title: 'Synthwave & Stories', listeners: '840 listening' },
  ]

  return (
    <div className="page dashboard">
      <header className="dash-header">
        <div className="brand">
          <div className="logo">▦</div>
          <div className="title">Pod Club</div>
        </div>
        <div className="avatar">E</div>
      </header>

      <section className="chips">
        <button className="chip active">All Rooms</button>
        <button className="chip">True Crime</button>
        <button className="chip">Music Lab</button>
        <button className="chip">Philosophy</button>
      </section>

      <section className="featured">
        <div className="featured-card">
          <div className="featured-top">
            <span className="badge">{featured.tag}</span>
            <span className="live">{featured.active}</span>
          </div>
          <h2>{featured.title}</h2>
          <p className="muted">{featured.subtitle}</p>

        </div>
      </section>

      <section className="trending">
        <div className="section-head">
          <h3>Trending Conversations</h3>
          <a className="see-all">See All</a>
        </div>
        <div className="trending-list">
          {trending.map((t, i) => (
            <article key={i} className="trending-card">
              <div className="thumb" />
              <div className="t-body">
                <div className="t-title">{t.title}</div>
                <div className="t-sub muted">with Sarah & Leo</div>
                <div className="t-bottom">
                  <div className="listeners"><span className="dot" aria-hidden></span><span className="text">{t.listeners}</span></div>
                  <button className="btn small">Listen</button>
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>

      <div style={{height: 120}} />

      <BottomNav />
    </div>
  )
}
