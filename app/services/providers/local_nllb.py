from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Any

from app.config import Settings
from app.language_map import get_language
from app.services.providers.base import TranslationProvider


@dataclass
class _ModelBundle:
    tokenizer: Any
    model: Any
    torch: Any
    device: str


class LocalNLLBProvider(TranslationProvider):
    provider_name = "local_nllb"

    def __init__(self, settings: Settings):
        self.settings = settings
        self.model_name = settings.model_name
        self._bundle: _ModelBundle | None = None
        self._lock = Lock()

    def is_model_loaded(self) -> bool:
        return self._bundle is not None

    def _load_bundle(self) -> _ModelBundle:
        if self._bundle is not None:
            return self._bundle

        with self._lock:
            if self._bundle is not None:
                return self._bundle

            try:
                import torch
                from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            except ImportError as exc:  # pragma: no cover - optional runtime dependency
                raise RuntimeError(
                    "Local NLLB translation requires `transformers`, `torch`, and `sentencepiece`. "
                    "Install dependencies from requirements.txt first."
                ) from exc

            requested_device = self.settings.model_device.lower().strip()
            if requested_device == "auto":
                device = "cuda" if torch.cuda.is_available() else "cpu"
            elif requested_device == "cuda" and not torch.cuda.is_available():
                device = "cpu"
            else:
                device = requested_device or "cpu"

            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            model.to(device)
            model.eval()

            self._bundle = _ModelBundle(
                tokenizer=tokenizer,
                model=model,
                torch=torch,
                device=device,
            )
            return self._bundle

    def translate_batch(self, texts: list[str], source_lang: str, target_lang: str) -> list[str]:
        if not texts:
            return []

        source = get_language(source_lang)
        target = get_language(target_lang)
        if source is None:
            raise ValueError(f"Unsupported source language: {source_lang}")
        if target is None:
            raise ValueError(f"Unsupported target language: {target_lang}")

        bundle = self._load_bundle()
        tokenizer = bundle.tokenizer
        model = bundle.model
        torch = bundle.torch
        device = bundle.device

        tokenizer.src_lang = source.provider_code
        outputs: list[str] = []

        batch_size = 8
        for index in range(0, len(texts), batch_size):
            batch = texts[index : index + batch_size]
            encoded = tokenizer(
                batch,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
            )
            encoded = {key: value.to(device) for key, value in encoded.items()}
            forced_bos_token_id = tokenizer.convert_tokens_to_ids(target.provider_code)

            with torch.no_grad():
                generated = model.generate(
                    **encoded,
                    forced_bos_token_id=forced_bos_token_id,
                    max_length=512,
                    num_beams=4,
                )

            outputs.extend(tokenizer.batch_decode(generated, skip_special_tokens=True))

        return outputs
