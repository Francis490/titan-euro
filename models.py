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
        if len(v) != 5: 
            raise ValueError("Servono esattamente 5 numeri principali")
        if any(not (1 <= n <= 50) for n in v): 
            raise ValueError("I numeri principali devono essere in [1, 50]")
        if len(set(v)) != len(v): 
            raise ValueError("I numeri principali non possono contenere duplicati")
        return sorted(v)

    @field_validator("euro_numbers")
    @classmethod
    def validate_euro_numbers(cls, v: List[int]) -> List[int]:
        if len(v) != 2: 
            raise ValueError("Servono esattamente 2 Euronumeri")
        if any(not (1 <= n <= 12) for n in v): 
            raise ValueError("Gli Euronumeri devono essere in [1, 12]")
        if len(set(v)) != len(v): 
            raise ValueError("Gli Euronumeri non possono contenere duplicati")
        return sorted(v)

    @model_validator(mode="after")
    def validate_disjoint_sets(self) -> "EurojackpotDraw":
        overlap = set(self.main_numbers) & set(self.euro_numbers)
        if overlap:
            raise ValueError(f"Numeri principali ed Euronumeri non possono sovrapporsi: {overlap}")
        return self
