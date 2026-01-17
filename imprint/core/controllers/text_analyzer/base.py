import collections
import hashlib
import math
import re
import uuid
from typing import Generator

from pydantic import BaseModel
from simhash import Simhash


class TextMetrics(BaseModel):
    text: str
    hash: str
    canvas_size: int
    chars_stats: list[tuple]
    symbols_count: int


class TextAnalyzerController:
    def __init__(
        self,
        n_gram_size: int = 3,
        word_shingle_size: int = 2,
        hash_dimension: int = 128,
        min_canvas_size: int = 1000,
        max_canvas_size: int = 8000,
    ):
        self.n_gram_size = n_gram_size
        self.word_shingle_size = word_shingle_size
        self.hash_dimension = hash_dimension
        self.min_canvas_size = min_canvas_size
        self.max_canvas_size = max_canvas_size
        # Предварительно компилируем паттерн для скорости
        self.word_regex = re.compile(r"\w+")

    def _get_features(self, text: str) -> Generator[str, None, None]:
        """
        Универсальный генератор признаков.
        Для коротких текстов (слово, фраза) использует n-граммы символов.
        Для длинных (предложение, книга) — шинглы слов.
        """
        length = len(text)

        # 1. Если это слово или очень короткая фраза (< 50 символов)
        if length < 50:
            yield from self._get_char_ngrams(text)

        # 2. Если это предложение или целая книга
        else:
            yield from self._get_word_shingles(text)

    def _get_char_ngrams(self, text: str) -> Generator[str, None, None]:
        """Символьные n-граммы через скользящее окно (быстро для коротких строк)"""
        clean_text = text.lower().strip()
        if len(clean_text) < self.n_gram_size:
            yield clean_text
            return

        for i in range(len(clean_text) - self.n_gram_size + 1):
            yield clean_text[i : i + self.n_gram_size]

    def _get_word_shingles(self, text: str) -> Generator[str, None, None]:
        """Шинглы слов через генератор (максимально экономно к памяти для книг)"""
        # finditer позволяет не копировать всю строку, а идти по ней итератором
        words = (m.group(0).lower() for m in self.word_regex.finditer(text))

        window = collections.deque(maxlen=self.word_shingle_size)

        for word in words:
            window.append(word)
            if len(window) == self.word_shingle_size:
                yield " ".join(window)

    def _calculate_canvas_size(self, text_len: int) -> int:
        """Рассчитывает размер холста от 1000 до 8000 на основе логарифма длины текста."""
        if text_len <= 100:
            return self.min_canvas_size

        # Логарифмический рост: log10(100)=2, log10(1,000,000)=6
        # Растягиваем диапазон [2, 6] до [1000, 8000]
        log_val = math.log10(text_len)
        scale = (log_val - 2) / (6 - 2)
        size = self.min_canvas_size + (
            self.max_canvas_size - self.min_canvas_size
        ) * max(0, min(1, scale))

        return int(size)

    def get_incremental_hash(self, text: str) -> str:
        parts = text.split()
        full_hash = ""

        for part in parts:
            part_hash = hashlib.md5(part.encode()).hexdigest()[:8]
            full_hash += part_hash

        return full_hash

    def analyze(self, text: str) -> TextMetrics:
        # SimHash
        hash = Simhash(self._get_features(text), f=self.hash_dimension)
        hash = f"{hash.value:x}"

        chars_stats = collections.Counter(text)
        sorted(chars_stats.items(), key=lambda item: ord(item[0]))

        return TextMetrics(
            text=text,
            hash=hash,
            canvas_size=self._calculate_canvas_size(len(text)),
            chars_stats=chars_stats.items(),
            symbols_count=len(text) if text else 1,
        )


if __name__ == "__main__":
    text_analyzer = TextAnalyzerController()

    for i in range(1, 5):
        text = str(uuid.uuid4()) * i

        data = text_analyzer.analyze(text)

        assert data
        assert data.hash

        print(f"Text: {text}, data: {data.model_dump_json()}")
