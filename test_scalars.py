from unittest.mock import MagicMock
# mock Result object
result = MagicMock()
# does result.scalars() return something that has .all()?
s = result.scalars()
print(f"Type of result.scalars(): {type(s)}")
print(f"Has all? {hasattr(s, 'all')}")
