from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Language:
    code: str
    label: str
    provider_code: str


# This starter map focuses on common languages. NLLB supports many more.
# Extend this dictionary as needed with additional FLORES-200 codes.
SUPPORTED_LANGUAGES: dict[str, Language] = {
    "sq": Language(code="sq", label="Albanian", provider_code="als_Latn"),
    "en": Language(code="en", label="English", provider_code="eng_Latn"),
    "de": Language(code="de", label="German", provider_code="deu_Latn"),
    "fr": Language(code="fr", label="French", provider_code="fra_Latn"),
    "it": Language(code="it", label="Italian", provider_code="ita_Latn"),
    "es": Language(code="es", label="Spanish", provider_code="spa_Latn"),
    "pt": Language(code="pt", label="Portuguese", provider_code="por_Latn"),
    "nl": Language(code="nl", label="Dutch", provider_code="nld_Latn"),
    "tr": Language(code="tr", label="Turkish", provider_code="tur_Latn"),
    "bs": Language(code="bs", label="Bosnian", provider_code="bos_Latn"),
    "hr": Language(code="hr", label="Croatian", provider_code="hrv_Latn"),
    "sr": Language(code="sr", label="Serbian", provider_code="srp_Cyrl"),
    "sl": Language(code="sl", label="Slovenian", provider_code="slv_Latn"),
    "mk": Language(code="mk", label="Macedonian", provider_code="mkd_Cyrl"),
    "ro": Language(code="ro", label="Romanian", provider_code="ron_Latn"),
    "el": Language(code="el", label="Greek", provider_code="ell_Grek"),
    "pl": Language(code="pl", label="Polish", provider_code="pol_Latn"),
    "cs": Language(code="cs", label="Czech", provider_code="ces_Latn"),
    "sk": Language(code="sk", label="Slovak", provider_code="slk_Latn"),
    "hu": Language(code="hu", label="Hungarian", provider_code="hun_Latn"),
    "sv": Language(code="sv", label="Swedish", provider_code="swe_Latn"),
    "no": Language(code="no", label="Norwegian Bokmal", provider_code="nob_Latn"),
    "da": Language(code="da", label="Danish", provider_code="dan_Latn"),
    "fi": Language(code="fi", label="Finnish", provider_code="fin_Latn"),
    "ru": Language(code="ru", label="Russian", provider_code="rus_Cyrl"),
    "uk": Language(code="uk", label="Ukrainian", provider_code="ukr_Cyrl"),
    "ar": Language(code="ar", label="Arabic", provider_code="arb_Arab"),
    "he": Language(code="he", label="Hebrew", provider_code="heb_Hebr"),
    "hi": Language(code="hi", label="Hindi", provider_code="hin_Deva"),
    "id": Language(code="id", label="Indonesian", provider_code="ind_Latn"),
    "ja": Language(code="ja", label="Japanese", provider_code="jpn_Jpan"),
    "ko": Language(code="ko", label="Korean", provider_code="kor_Hang"),
    "zh": Language(code="zh", label="Chinese (Simplified)", provider_code="zho_Hans"),
    "zh-hant": Language(code="zh-hant", label="Chinese (Traditional)", provider_code="zho_Hant"),
}

ALIASES: dict[str, str] = {
    "alb": "sq",
    "al": "sq",
    "english": "en",
    "german": "de",
    "french": "fr",
    "italian": "it",
    "spanish": "es",
    "turkish": "tr",
    "serbian": "sr",
    "croatian": "hr",
    "bosnian": "bs",
    "macedonian": "mk",
    "romanian": "ro",
    "greek": "el",
    "chinese": "zh",
    "japanese": "ja",
    "korean": "ko",
}


def normalize_language_code(code: str) -> str:
    normalized = code.strip().lower().replace("_", "-")
    return ALIASES.get(normalized, normalized)


def get_language(code: str) -> Language | None:
    return SUPPORTED_LANGUAGES.get(normalize_language_code(code))


def list_languages() -> list[Language]:
    return list(SUPPORTED_LANGUAGES.values())
