from __future__ import annotations

from datetime import datetime
from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class TitleType(str, Enum):
    movie = "movie"
    tv = "tv"


class ProviderRef(BaseModel):
    provider: str
    id: str


class TitleSummary(BaseModel):
    ref: ProviderRef
    type: TitleType
    title: str
    year: int | None = None
    poster_url: str | None = None


class SearchResponse(BaseModel):
    results: list[TitleSummary]


class Person(BaseModel):
    id: str
    name: str
    role: str | None = None
    character: str | None = None


class CreditsResponse(BaseModel):
    ref: ProviderRef
    cast: list[Person] = Field(default_factory=list)
    crew: list[Person] = Field(default_factory=list)


class Rating(BaseModel):
    source: str
    value: float = Field(ge=0, le=10)
    votes: int | None = Field(default=None, ge=0)


class RatingsResponse(BaseModel):
    ref: ProviderRef
    ratings: list[Rating] = Field(default_factory=list)


class Video(BaseModel):
    site: str
    key: str
    name: str | None = None
    type: str | None = None
    url: str | None = None


class VideosResponse(BaseModel):
    ref: ProviderRef
    videos: list[Video] = Field(default_factory=list)


class TitleDetails(BaseModel):
    ref: ProviderRef
    type: TitleType
    title: str
    original_title: str | None = None
    overview: str | None = None
    release_date: date | None = None
    runtime_minutes: int | None = Field(default=None, ge=0)
    genres: list[str] = Field(default_factory=list)
    poster_url: str | None = None
    backdrop_url: str | None = None


class TitleFullResponse(BaseModel):
    title: TitleDetails
    credits: CreditsResponse | None = None
    ratings: RatingsResponse | None = None
    trailers: VideosResponse | None = None


class KnownForTitle(BaseModel):
    ref: ProviderRef
    type: TitleType
    title: str
    role: str | None = None
    character: str | None = None
    year: int | None = None
    poster_url: str | None = None


class PersonProfile(BaseModel):
    ref: ProviderRef
    name: str
    biography: str | None = None
    birthday: date | None = None
    profile_url: str | None = None
    known_for: list[KnownForTitle] = Field(default_factory=list)


class RecommendationsResponse(BaseModel):
    ref: ProviderRef
    results: list[TitleSummary] = Field(default_factory=list)


class Review(BaseModel):
    author: str
    content: str
    rating: float | None = Field(default=None, ge=0, le=10)
    created_at: datetime | None = None
    url: str | None = None


class ReviewsResponse(BaseModel):
    ref: ProviderRef
    results: list[Review] = Field(default_factory=list)
