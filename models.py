"""Modelli Pydantic per la validazione severa dei dati Eurojackpot."""

from datetime import date, datetime
from typing import List
from pydantic import BaseModel, Field, field_validator, model_validator

class EurojackpotDraw(BaseModel):
    draw_date: date
    main_numbers: List[int] = Field(..., min_length=5, max_length=5)
    euro_numbers: List[int] = Field(..., min_length=2, max_length=2)
    source: str = "multipasko.pl"
    fetched_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("main_numbers")
    @classmethod
    def validate_main_numbers(cls, v: List[int]) -> List[int]:
        if len(v) != 5: raise ValueError("Servono 5 numeri")
        if any(not (1 <= n <= 50) for n in v): raise ValueError("Range 1-50")
        if len(set(v)) != len(v): raise ValueError("Duplicati")
        return sorted(v)

    @field_validator("euro_numbers")
    @classmethod
    def validate_euro_numbers(cls, v: List[int]) -> List[int]:
        if len(v) != 2: raise ValueError("Servono 2 euronumeri")
        if any(not (1 <= n <= 10) for n in v): raise ValueError("Range 1-10")
        if len(set(v)) != len(v): raise ValueError("Duplicati")
        return sorted(v)

    @model_validator(mode="after")
    def validate_disjoint_sets(self) -> "EurojackpotDraw":
        overlap = set(self.main_numbers) & set(self.euro_numbers)
        if overlap: raise ValueError(f"Overlap: {overlap}")
        return self
