class TestBookmark:
    url = "/api/v1/bookmark"

    sort_keys = {
        "BY_ID": "id",
        "BY_DATE": "dt_created",
        "BY_TITLE": "title",
        "BY_LINK": "link"
    }

    async def retrieve_using_sort(self, client, data_sample_bookmark, auth_header, sort_key):
        response = await client.get(url=self.url + "?sort_key=" + sort_key, headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        attr = self.sort_keys[sort_key]
        items_id = [item[attr] for item in data["items"]]
        return items_id == sorted(items_id)

    async def test_create(self, client, auth_header):
        data = {"link": "https://ya.ru/"}
        response = await client.post(url=self.url, json=data, headers=auth_header)
        assert response.status_code == 201, "POST create doesn't work"

    async def test_create_using_tag(self, client, auth_header):
        data = {"link": "https://ya.ru/",
                "tag": "example_tag"
                }
        response = await client.post(url=self.url, json=data, headers=auth_header)
        assert response.status_code == 201, "POST create doesn't work"

    async def test_retrieve(self, client, data_sample_bookmark, auth_header):
        response = await client.get(url=self.url, headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert str(data_sample_bookmark.id) in [data["items"][0]["id"], data["items"][1]["id"]]
        assert len(data["items"]) == 2

    async def test_retrieve_unauth(self, client, data_sample_bookmark):
        response = await client.get(url=self.url)
        assert response.status_code == 401

    async def test_retrieve_tag(self, client, data_sample_bookmark, auth_header):
        response = await client.get(url=self.url + "?tag=example", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert str(data_sample_bookmark.id) in [data["items"][0]["id"], data["items"][1]["id"]]
        assert len(data["items"]) == 2
    async def test_all_sort_keys(self, client, data_sample_bookmark, auth_header):
        passed = True
        for sort_key in self.sort_keys:
            passed &= await self.retrieve_using_sort(client, data_sample_bookmark, auth_header, sort_key)
        assert passed
    async def test_retrieve_get_by_id(self, client, data_sample_bookmark, auth_header):
        response = await client.get(url=self.url + "/" + str(data_sample_bookmark.id), headers=auth_header)
        assert response.status_code == 200

    async def test_retrieve_get_by_id_not_found(self, client, auth_header):
        response = await client.get(url=self.url + "/2998c216-ccab-4e4e-8485-bb2c67bbc119", headers=auth_header)
        assert response.status_code == 404

    async def test_delete(self, client, data_sample_bookmark, auth_header):
        response = await client.delete(url=self.url + "/" + str(data_sample_bookmark.id), headers=auth_header)
        assert response.status_code == 204
