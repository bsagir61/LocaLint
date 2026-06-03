from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from localint.locales import normalize_locale_code


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


class Issue(BaseModel):
    severity: Severity
    key: str = ""
    locale: str = ""
    check: str
    message: str
    suggestion: str = ""
    source_text: str = ""
    target_text: str = ""


class LocalizationRow(BaseModel):
    key: str
    translations: dict[str, str] = Field(default_factory=dict)
    row_number: int | None = None


class LocalizationTable(BaseModel):
    rows: list[LocalizationRow]
    languages: list[str]
    file_format: str = "unknown"
    source_language: str = "en"
    columns: list[str] = Field(default_factory=list)
    ignored_columns: list[str] = Field(default_factory=list)
    duplicate_keys: list[str] = Field(default_factory=list)
    encoding_warnings: list[str] = Field(default_factory=list)
    shape_warnings: list[str] = Field(default_factory=list)
    source_name: str = "uploaded file"

    @property
    def total_keys(self) -> int:
        return len(self.rows)

    def target_languages(self, source_language: str | None = None) -> list[str]:
        source = source_language or self.source_language
        source_normalized = normalize_locale_code(source)
        return [
            language
            for language in self.languages
            if language != source and normalize_locale_code(language) != source_normalized
        ]
