// extract_channel.js
//
// Run this via mcp__Claude_in_Chrome__javascript_tool on a Slack channel tab.
// It scrolls the virtual message list to force rendering, then extracts each
// visible parent message's text, author, timestamp, and thread reply count.
//
// Returns a JSON string: { channel, messages: [{author, ts, text, replies, permalink}] }
// sorted by reply count descending.
//
// Usage pattern from the caller:
//   1. Navigate the tab to https://app.slack.com/client/<WS>/<CHANNEL_ID>
//   2. Wait ~2s
//   3. Paste the body of this file as the `text` arg to javascript_tool
//   4. Parse the returned string as JSON
//
// Slack's DOM hooks change occasionally. If this stops working, the fragile
// selectors to update are:
//   - .c-virtual_list__scroll_container (message scroller)
//   - [data-qa="message_container"]    (one message)
//   - [data-qa="message_sender_name"]  (author)
//   - [data-qa="reply_bar_count"] or [data-qa="threads_view_reply_count"] (reply count)

new Promise((resolve) => {
  const SCROLL_PASSES = 3;          // how many times to scroll up to load older messages
  const SCROLL_PAUSE_MS = 600;

  const scroller = document.querySelector('.c-virtual_list__scroll_container');
  if (!scroller) {
    resolve(JSON.stringify({ error: 'no scroller found; is this a channel view?' }));
    return;
  }

  // Channel name from the page title or header
  const channelName = (document.title.match(/^([^()]+)/) || [, 'unknown'])[1].trim()
    .replace(/ - ClassDojo.*$/, '')
    .replace(/ \(Channel\)/, '');

  let pass = 0;
  function scrollPass() {
    if (pass >= SCROLL_PASSES) {
      scroller.scrollTop = scroller.scrollHeight; // back to bottom
      setTimeout(harvest, SCROLL_PAUSE_MS);
      return;
    }
    // Scroll a big chunk up to trigger older-message loading
    scroller.scrollTop = Math.max(0, scroller.scrollTop - scroller.clientHeight * 2);
    pass += 1;
    setTimeout(scrollPass, SCROLL_PAUSE_MS);
  }

  function harvest() {
    const nodes = document.querySelectorAll('[data-qa="message_container"]');
    const out = [];
    nodes.forEach((n) => {
      // Author
      let author = '';
      const a = n.querySelector('[data-qa="message_sender_name"], [data-qa="message_sender"]');
      if (a) author = (a.innerText || '').trim();

      // Timestamp
      let ts = '';
      const tEl = n.querySelector('.c-timestamp, [data-qa="timestamp"]');
      if (tEl) ts = (tEl.getAttribute('data-ts') || tEl.getAttribute('aria-label') || tEl.innerText || '').trim();

      // Body text — strip reactions/reply-bar copies
      let text = (n.innerText || '').replace(/\s+/g, ' ').trim();
      // Cut trailing reply bar & reactions; they live after the message body
      text = text.replace(/\s*\d+\s+repl(y|ies).*$/i, '').trim();

      // Reply count
      let replies = 0;
      const rcEl = n.querySelector('[data-qa="reply_bar_count"], [data-qa="threads_view_reply_count"]');
      if (rcEl) {
        const m = (rcEl.innerText || '').match(/\d+/);
        if (m) replies = parseInt(m[0], 10);
      } else {
        // Fallback: look for "N replies" in the message innerText
        const m = (n.innerText || '').match(/(\d+)\s+repl(y|ies)/i);
        if (m) replies = parseInt(m[1], 10);
      }

      // Thread permalink — grab from the reply bar link if present
      let permalink = '';
      const link = n.querySelector('a[href*="thread_ts="], a[href*="/archives/"]');
      if (link) permalink = link.href;

      if (text.length > 0) {
        out.push({ author, ts, text: text.slice(0, 1200), replies, permalink });
      }
    });

    // Dedupe by (author+ts+first-60-chars) in case of re-renders
    const seen = new Set();
    const unique = [];
    for (const m of out) {
      const key = `${m.author}|${m.ts}|${m.text.slice(0, 60)}`;
      if (!seen.has(key)) { seen.add(key); unique.push(m); }
    }

    unique.sort((a, b) => b.replies - a.replies);

    resolve(JSON.stringify({
      channel: channelName,
      url: location.href,
      captured: unique.length,
      messages: unique,
    }));
  }

  scrollPass();
});
