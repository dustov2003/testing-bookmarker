from bookmarker.utils.user import get_current_user, authenticate_user, verify_password, create_access_token


class TestBusinessLogic:

    async def test_get_current_user(self, migrated_postgres, session, jwt_token, data_sample_user):
        user = await get_current_user(session, jwt_token)
        assert user.id == data_sample_user.id

    async def test_authenticate_user(self, migrated_postgres, session, data_sample_user):
        user = await authenticate_user(session, data_sample_user.username, "striiiing")
        assert user != False

    def test_verify_password(self, migrated_postgres, data_sample_user):
        assert not verify_password("wrong_pass", data_sample_user.password)
