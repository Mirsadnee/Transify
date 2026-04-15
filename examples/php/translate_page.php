<?php

declare(strict_types=1);

function translate_html_via_api(string $html, string $targetLang, string $sourceLang = 'auto'): string
{
    $apiBase = 'http://127.0.0.1:8000';
    $apiKey = ''; // optional

    $payload = json_encode([
        'html' => $html,
        'source_lang' => $sourceLang,
        'target_lang' => $targetLang,
    ], JSON_UNESCAPED_UNICODE);

    if ($payload === false) {
        throw new RuntimeException('Failed to encode translation payload.');
    }

    $ch = curl_init($apiBase . '/translate-html');
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_HTTPHEADER => array_filter([
            'Content-Type: application/json',
            $apiKey !== '' ? 'X-API-Key: ' . $apiKey : null,
        ]),
        CURLOPT_POSTFIELDS => $payload,
        CURLOPT_TIMEOUT => 120,
    ]);

    $response = curl_exec($ch);
    if ($response === false) {
        $error = curl_error($ch);
        curl_close($ch);
        throw new RuntimeException('Translation request failed: ' . $error);
    }

    $statusCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    $data = json_decode($response, true);
    if (!is_array($data)) {
        throw new RuntimeException('Invalid JSON response from translator API.');
    }

    if ($statusCode >= 400) {
        $detail = $data['detail'] ?? 'Unknown API error';
        throw new RuntimeException('Translator API error: ' . $detail);
    }

    return (string)($data['translated_html'] ?? $html);
}

// Example usage in a PHP site.
$lang = $_GET['lang'] ?? 'sq';

ob_start();
?>
<!DOCTYPE html>
<html lang="sq">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Faqja ime</title>
</head>
<body>
  <nav>
    <a href="?lang=sq">Shqip</a> |
    <a href="?lang=en">English</a> |
    <a href="?lang=de">Deutsch</a>
  </nav>

  <h1>Mirë se vini</h1>
  <p>Kjo është faqja ime e ndërtuar në PHP.</p>
  <button>Na kontaktoni</button>
  <div translate="no">BrandName</div>
</body>
</html>
<?php
$html = ob_get_clean();

if ($lang === 'sq') {
    echo $html;
    exit;
}

try {
    echo translate_html_via_api($html, $lang, 'sq');
} catch (Throwable $e) {
    http_response_code(500);
    echo '<pre>' . htmlspecialchars($e->getMessage(), ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '</pre>';
}
