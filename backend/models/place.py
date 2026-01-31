"""Place model for representing places with vibe categorization"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Place:
    """Represents a place with its vibe categorizations"""
    place_id: str
    name: str
    latitude: float
    longitude: float
    google_type: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    categorization_source: str = 'static'  # 'static' or 'llm'
    last_updated: Optional[datetime] = None
    vibes: List[str] = field(default_factory=list)

    def get_vibes(self) -> List[str]:
        """Returns list of vibes this place belongs to"""
        return self.vibes

    def has_vibe(self, vibe: str) -> bool:
        """Check if place belongs to a specific vibe"""
        return vibe in self.vibes

    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            'place_id': self.place_id,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'google_type': self.google_type,
            'address': self.address,
            'rating': self.rating,
            'user_ratings_total': self.user_ratings_total,
            'categorization_source': self.categorization_source,
            'vibes': self.vibes
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Place':
        """Create Place from dictionary"""
        return cls(
            place_id=data['place_id'],
            name=data['name'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            google_type=data.get('google_type'),
            address=data.get('address'),
            rating=data.get('rating'),
            user_ratings_total=data.get('user_ratings_total'),
            categorization_source=data.get('categorization_source', 'static'),
            vibes=data.get('vibes', [])
        )

    @classmethod
    def from_db_row(cls, row, vibes: List[str] = None) -> 'Place':
        """Create Place from database row"""
        return cls(
            place_id=row['place_id'],
            name=row['name'],
            latitude=row['latitude'],
            longitude=row['longitude'],
            google_type=row['google_type'],
            address=row['address'],
            rating=row['rating'],
            user_ratings_total=row['user_ratings_total'],
            categorization_source=row['categorization_source'],
            vibes=vibes or []
        )
