(() => {
  const form = document.getElementById('contact-form');
  const status = document.getElementById('contact-status');
  if (!form || !status) return;

  function setStatus(text) {
    status.textContent = text;
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const data = new FormData(form);
    const payload = {
      name: String(data.get('name') || '').trim(),
      email: String(data.get('email') || '').trim(),
      project: String(data.get('project') || '').trim(),
      message: String(data.get('message') || '').trim(),
    };

    if (!payload.name || !payload.email || !payload.message) {
      setStatus('PLEASE FILL REQUIRED FIELDS');
      return;
    }

    setStatus('SENDING...');

    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const json = await res.json().catch(() => ({}));
      if (!res.ok || !json.success) {
        setStatus('ERROR. TRY AGAIN.');
        return;
      }

      form.reset();
      setStatus('SENT. I WILL REPLY SOON.');
    } catch {
      setStatus('NETWORK ERROR.');
    }
  });
})();

