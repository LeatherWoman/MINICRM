from fastapi import status


class TestLeads:
    """Тесты для эндпоинтов лидов"""

    def test_create_lead(self, client, sample_lead_data):
        """Тест создания лида"""
        response = client.post("/api/v1/leads/", json=sample_lead_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["external_id"] == sample_lead_data["external_id"]
        assert data["phone"] == sample_lead_data["phone"]
        assert data["email"] == sample_lead_data["email"]
        assert data["full_name"] == sample_lead_data["full_name"]
        assert data["notes"] == sample_lead_data["notes"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_lead_duplicate_external_id(self, client, sample_lead_data):
        """Тест создания лида с дублирующимся external_id"""
        # Первое создание
        client.post("/api/v1/leads/", json=sample_lead_data)

        # Второе создание с тем же external_id
        response = client.post("/api/v1/leads/", json=sample_lead_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]

    def test_get_leads(self, client, sample_lead_data):
        """Тест получения списка лидов"""
        # Создаем несколько лидов
        for i in range(3):
            lead_data = sample_lead_data.copy()
            lead_data["external_id"] = f"user_{i}"
            lead_data["email"] = f"user{i}@test.com"
            client.post("/api/v1/leads/", json=lead_data)

        response = client.get("/api/v1/leads/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert isinstance(data, list)
        assert len(data) >= 3

    def test_get_lead_by_id(self, client, sample_lead_data):
        """Тест получения лида по ID"""
        # Создаем лида
        create_response = client.post("/api/v1/leads/", json=sample_lead_data)
        lead_id = create_response.json()["id"]

        # Получаем лида
        response = client.get(f"/api/v1/leads/{lead_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == lead_id
        assert data["external_id"] == sample_lead_data["external_id"]

    def test_get_nonexistent_lead(self, client):
        """Тест получения несуществующего лида"""
        response = client.get("/api/v1/leads/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_lead(self, client, sample_lead_data):
        """Тест обновления лида"""
        # Создаем лида
        create_response = client.post("/api/v1/leads/", json=sample_lead_data)
        lead_id = create_response.json()["id"]

        # Обновляем лида
        update_data = {
            "phone": "+79169876543",
            "notes": "Обновленные заметки",
            "full_name": "Обновленное Имя",
        }

        response = client.put(f"/api/v1/leads/{lead_id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["phone"] == update_data["phone"]
        assert data["notes"] == update_data["notes"]
        assert data["full_name"] == update_data["full_name"]
        # Проверяем, что external_id не изменился
        assert data["external_id"] == sample_lead_data["external_id"]

    def test_update_lead_partial(self, client, sample_lead_data):
        """Тест частичного обновления лида"""
        # Создаем лида
        create_response = client.post("/api/v1/leads/", json=sample_lead_data)
        lead_id = create_response.json()["id"]

        # Обновляем только телефон
        update_data = {"phone": "+79161111111"}

        response = client.put(f"/api/v1/leads/{lead_id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["phone"] == update_data["phone"]
        # Проверяем, что остальные поля не изменились
        assert data["email"] == sample_lead_data["email"]
        assert data["full_name"] == sample_lead_data["full_name"]

    def test_update_nonexistent_lead(self, client):
        """Тест обновления несуществующего лида"""
        update_data = {"phone": "+79161111111"}
        response = client.put("/api/v1/leads/999", json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
