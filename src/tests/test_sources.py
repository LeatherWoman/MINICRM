from fastapi import status


class TestSources:
    """Тесты для эндпоинтов источников"""

    def test_create_source(self, client, sample_source_data):
        """Тест создания источника"""
        response = client.post("/api/v1/sources/", json=sample_source_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["name"] == sample_source_data["name"]
        assert data["bot_token"] == sample_source_data["bot_token"]
        assert data["description"] == sample_source_data["description"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_source_duplicate_bot_token(self, client, sample_source_data):
        """Тест создания источника с дублирующимся bot_token"""
        # Первое создание
        client.post("/api/v1/sources/", json=sample_source_data)

        # Второе создание с тем же bot_token
        response = client.post("/api/v1/sources/", json=sample_source_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]

    def test_get_sources(self, client, sample_source_data):
        """Тест получения списка источников"""
        # Создаем несколько источников
        for i in range(3):
            source_data = sample_source_data.copy()
            source_data["bot_token"] = f"bot_token_{i}"
            source_data["name"] = f"Источник {i}"
            client.post("/api/v1/sources/", json=source_data)

        response = client.get("/api/v1/sources/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert isinstance(data, list)
        assert len(data) >= 3

    def test_get_source_by_id(self, client, sample_source_data):
        """Тест получения источника по ID"""
        # Создаем источник
        create_response = client.post("/api/v1/sources/", json=sample_source_data)
        source_id = create_response.json()["id"]

        # Получаем источник
        response = client.get(f"/api/v1/sources/{source_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == source_id
        assert data["name"] == sample_source_data["name"]
        assert "weights" in data

    def test_add_source_weight(self, client, sample_operator_data, sample_source_data):
        """Тест добавления веса оператора к источнику"""
        # Создаем оператора
        operator_response = client.post("/api/v1/operators/", json=sample_operator_data)
        operator_id = operator_response.json()["id"]

        # Создаем источник
        source_response = client.post("/api/v1/sources/", json=sample_source_data)
        source_id = source_response.json()["id"]

        # Добавляем вес
        weight_data = {"operator_id": operator_id, "weight": 50}

        response = client.post(f"/api/v1/sources/{source_id}/weights", json=weight_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["source_id"] == source_id
        assert data["operator_id"] == operator_id
        assert data["weight"] == weight_data["weight"]

    def test_add_source_weight_to_nonexistent_source(
        self, client, sample_operator_data
    ):
        """Тест добавления веса к несуществующему источнику"""
        operator_response = client.post("/api/v1/operators/", json=sample_operator_data)
        operator_id = operator_response.json()["id"]

        weight_data = {"operator_id": operator_id, "weight": 50}
        response = client.post("/api/v1/sources/999/weights", json=weight_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_source_with_weights(
        self, client, sample_operator_data, sample_source_data
    ):
        """Тест получения источника с весами"""
        # Создаем оператора
        operator_response = client.post("/api/v1/operators/", json=sample_operator_data)
        operator_id = operator_response.json()["id"]

        # Создаем источник
        source_response = client.post("/api/v1/sources/", json=sample_source_data)
        source_id = source_response.json()["id"]

        # Добавляем вес
        weight_data = {"operator_id": operator_id, "weight": 50}
        client.post(f"/api/v1/sources/{source_id}/weights", json=weight_data)

        # Получаем источник с весами
        response = client.get(f"/api/v1/sources/{source_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "weights" in data
        assert isinstance(data["weights"], list)
        assert len(data["weights"]) == 1
        assert data["weights"][0]["operator_id"] == operator_id
        assert data["weights"][0]["weight"] == 50

    def test_remove_source_weight(
        self, client, sample_operator_data, sample_source_data
    ):
        """Тест удаления веса источника"""
        # Создаем оператора
        operator_response = client.post("/api/v1/operators/", json=sample_operator_data)
        operator_id = operator_response.json()["id"]

        # Создаем источник
        source_response = client.post("/api/v1/sources/", json=sample_source_data)
        source_id = source_response.json()["id"]

        # Добавляем вес
        weight_data = {"operator_id": operator_id, "weight": 50}
        client.post(f"/api/v1/sources/{source_id}/weights", json=weight_data)

        # Удаляем вес
        response = client.delete(f"/api/v1/sources/{source_id}/weights/{operator_id}")

        assert response.status_code == status.HTTP_200_OK
        assert "removed" in response.json()["message"].lower()

        # Проверяем, что вес удален
        source_response = client.get(f"/api/v1/sources/{source_id}")
        assert len(source_response.json()["weights"]) == 0

    def test_remove_nonexistent_weight(self, client, sample_source_data):
        """Тест удаления несуществующего веса"""
        # Создаем источник
        source_response = client.post("/api/v1/sources/", json=sample_source_data)
        source_id = source_response.json()["id"]

        response = client.delete(f"/api/v1/sources/{source_id}/weights/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
