class TestUser:

    url = "/api/v1/user/"

    async def test_registration(self, client):
        reg_data = {"username": "string", "password": "striiiing", "email": "user@example.com"}
        response = await client.post(url=self.url + "registration", json=reg_data)
        assert response.status_code == 201, "POST registration doesn't work"

    async def test_registration_user_already_exist(self, client, data_sample_user):
        reg_data = {"username": "string", "password": "striiiing", "email": "user@example.com"}
        response = await client.post(url=self.url + "registration", json=reg_data)
        assert response.status_code == 400

    async def test_registration_password_too_short(self, client):
        reg_data = {"username": "string", "password": "string", "email": "user@example.com"}
        response = await client.post(url=self.url + "registration", json=reg_data)
        assert response.status_code == 400
        assert response.json()["detail"] == "The password is too short. The minimum password length should be 8"

    async def test_authentication(self, client, data_sample_user):

        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"username": "string", "password": "striiiing"}
        response = await client.post(url=self.url + "authentication", data=data, headers=headers)
        assert response.status_code == 200, "POST authentication doesn't work"

    async def test_authentication_unauthorized(self, client):

        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"username": "string", "password": "string"}
        response = await client.post(url=self.url + "authentication", data=data, headers=headers)
        assert response.status_code == 401

    async def test_me(self, client, auth_header):
        response = await client.get(url=self.url + "me", headers=auth_header)
        assert response.status_code == 200, "GET me  doesn't work"

    async def test_takeout(self, client, auth_header):
        response = await client.delete(url=self.url + "takeout", headers=auth_header)
        assert response.status_code == 204, "DELETE takeout  doesn't work"
