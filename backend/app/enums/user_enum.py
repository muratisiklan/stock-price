from enum import Enum


class UserRole(str,Enum):
    ADMIN = "admin"
    PLEB = "pleb"
    INVESTOR = "investor"