from enum import Enum


class ReservationType(str, Enum):
    PERMANENT_RESIDENCE_PERMIT = 'permanent-residence-permit'
    FAMILY_FIRST_AND_EXTENDED_RESIDENCE_PERMIT = 'family-first-and-extended-residence-permit'
