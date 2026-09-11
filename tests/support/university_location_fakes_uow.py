from camp_match.shared_kernel.application.unit_of_work import UnitOfWork

class FakeUnitOfWork(UnitOfWork):
    async def __aenter__(self) -> UnitOfWork:
        return self
    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        pass
    async def commit(self) -> None:
        pass
    async def rollback(self) -> None:
        pass
