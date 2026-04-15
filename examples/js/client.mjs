const apiBase = 'http://127.0.0.1:8000';
const apiKey = ''; // optional

async function translateText(text, sourceLang, targetLang) {
  const response = await fetch(`${apiBase}/translate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(apiKey ? { 'X-API-Key': apiKey } : {}),
    },
    body: JSON.stringify({
      text,
      source_lang: sourceLang,
      target_lang: targetLang,
    }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Translation failed');
  }

  return data.translated;
}

async function translateHtml(html, sourceLang, targetLang) {
  const response = await fetch(`${apiBase}/translate-html`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(apiKey ? { 'X-API-Key': apiKey } : {}),
    },
    body: JSON.stringify({
      html,
      source_lang: sourceLang,
      target_lang: targetLang,
    }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'HTML translation failed');
  }

  return data.translated_html;
}

async function main() {
  const translated = await translateText('Mirë se vini në faqen time', 'sq', 'en');
  console.log('Translated text:', translated);

  const html = '<h1>Mirë se vini</h1><p>Kjo është faqja ime.</p>';
  const translatedHtml = await translateHtml(html, 'sq', 'en');
  console.log('Translated HTML:', translatedHtml);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
