
class TestAppHealth:

    url = "/api/v1/health_check/"

    async def test_ping_app(self, client, auth_header):
        response = await client.get(url=self.url + "ping_application", headers=auth_header)
        assert response.status_code == 200, "GET ping_application doesn't work"
        assert response.json()["message"] == "Application worked!"

    async def test_ping_db(self, client, auth_header):
        response = await client.get(url=self.url + "ping_database", headers=auth_header)
        assert response.status_code == 200, "GET ping_database doesn't work"
        assert response.json()["message"] == "Database worked!"
