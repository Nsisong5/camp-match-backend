from camp_match.modules.search.application.ports.outbound import UniversityLocationProvider
from camp_match.modules.university_location.application.ports.inbound import UniversityLocationQueryPort
from camp_match.modules.search.domain.value_objects import Coordinates, EntityId

class UniversityLocationProviderAdapter(UniversityLocationProvider):
    def __init__(self, query_port: UniversityLocationQueryPort):
        self._query_port = query_port

    async def get_campus_coordinates(self, campus_id: EntityId) -> Coordinates | None:
        location = await self._query_port.get_campus_location(str(campus_id))
        if not location:
            return None
        return Coordinates(latitude=location.latitude, longitude=location.longitude)
