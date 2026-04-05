from app.modules.users.repos import UserRepo


class AdminListUsers:
    def __init__(self, repo: UserRepo):
        self.repo = repo

    async def execute(self, offset: int, limit: int):
        return await self.repo.list(offset, limit)
