from camp_match.modules.profile.domain.value_objects import (
    ProfileType,
    ScoutProfileDetails,
    StudentProfileDetails,
)
from camp_match.shared_kernel.domain.identifiers import EntityId


class Profile:
    def __init__(
        self,
        id: EntityId,
        identity_id: EntityId,
        display_name: str,
        student_details: StudentProfileDetails | None = None,
        scout_details: ScoutProfileDetails | None = None,
        bio: str | None = None,
        phone_number: str | None = None,
        avatar_url: str | None = None,
        avatar_media_id: EntityId | None = None,
    ) -> None:
        if not (1 <= len(display_name.strip()) <= 100):
            raise ValueError("display_name must be 1–100 characters")
        
        if (student_details is None and scout_details is None) or (
            student_details is not None and scout_details is not None
        ):
            raise ValueError("Exactly one of student_details or scout_details must be provided")
        
        self._id = id
        self._identity_id = identity_id
        self._display_name = display_name.strip()
        self._bio = bio
        self._phone_number = phone_number
        self._avatar_url = avatar_url
        self._avatar_media_id = avatar_media_id
        
        if student_details:
            self._profile_type = ProfileType.STUDENT
            self._student_details = student_details
            self._scout_details = None
        else:
            self._profile_type = ProfileType.SCOUT
            self._student_details = None
            self._scout_details = scout_details # type: ignore

    @property
    def id(self) -> EntityId: return self._id

    @property
    def identity_id(self) -> EntityId: return self._identity_id

    @property
    def profile_type(self) -> ProfileType: return self._profile_type

    @property
    def display_name(self) -> str: return self._display_name

    @property
    def bio(self) -> str | None: return self._bio

    @property
    def phone_number(self) -> str | None: return self._phone_number

    @property
    def avatar_url(self) -> str | None: return self._avatar_url

    @property
    def avatar_media_id(self) -> EntityId | None: return self._avatar_media_id

    @property
    def completeness_percentage(self) -> float:
        core_fields = [self._bio, self._phone_number, self._avatar_url or self._avatar_media_id]
        if self._profile_type == ProfileType.STUDENT and self._student_details:
            details_fields = [
                self._student_details.university_name,
                self._student_details.department,
                self._student_details.budget_min_naira,
                self._student_details.budget_max_naira,
                self._student_details.preferred_accommodation_type,
                self._student_details.cleanliness_preference,
                self._student_details.sleep_schedule,
            ]
        elif self._profile_type == ProfileType.SCOUT and self._scout_details:
            details_fields = [
                self._scout_details.business_name,
                self._scout_details.business_description,
                self._scout_details.years_active,
                self._scout_details.availability_status,
            ]
        else:
            details_fields = []
            
        all_fields = core_fields + details_fields
        if not all_fields:
            return 0.0
        
        non_null_fields = [f for f in all_fields if f is not None]
        return (len(non_null_fields) / len(all_fields)) * 100

    @property
    def student_details(self) -> StudentProfileDetails | None: return self._student_details

    @property
    def scout_details(self) -> ScoutProfileDetails | None: return self._scout_details

    def update_core(
        self,
        display_name: str | None = None,
        bio: str | None = None,
        phone_number: str | None = None,
        avatar_url: str | None = None,
    ) -> None:
        if display_name is not None:
            if not (1 <= len(display_name.strip()) <= 100):
                raise ValueError("display_name must be 1–100 characters")
            self._display_name = display_name.strip()
        if bio is not None:
            self._bio = bio
        if phone_number is not None:
            self._phone_number = phone_number
        if avatar_url is not None:
            self._avatar_url = avatar_url
            self._avatar_media_id = None

    def set_avatar_media(self, media_id: EntityId) -> None:
        self._avatar_media_id = media_id
        self._avatar_url = None

    def update_student_details(self, details: StudentProfileDetails) -> None:
        if self._profile_type != ProfileType.STUDENT:
            raise ValueError("Cannot update student details on a non-student profile")
        self._student_details = details

    def update_scout_details(self, details: ScoutProfileDetails) -> None:
        if self._profile_type != ProfileType.SCOUT:
            raise ValueError("Cannot update scout details on a non-scout profile")
        self._scout_details = details
