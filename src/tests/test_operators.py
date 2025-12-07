from fastapi import status


class TestOperators:
    """Тесты для эндпоинтов операторов"""

    def test_create_operator(self, client, sample_operator_data):
        """Тест создания оператора"""
        response = client.post("/api/v1/operators/", json=sample_operator_data)

        # Отладка
        if response.status_code != status.HTTP_200_OK:
            print(f"Error creating operator: {response.json()}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["name"] == sample_operator_data["name"]
        assert data["email"] == sample_operator_data["email"]
        assert data["max_load"] == sample_operator_data["max_load"]
        assert data["is_active"] == sample_operator_data["is_active"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

        return data["id"]  # Возвращаем ID для использования в других тестах

    def test_create_operator_duplicate_email(self, client, sample_operator_data):
        """Тест создания оператора с дублирующимся email"""
        # Первое создание
        client.post("/api/v1/operators/", json=sample_operator_data)

        # Второе создание с тем же email
        response = client.post("/api/v1/operators/", json=sample_operator_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]

    def test_get_operators(self, client):
        """Тест получения списка операторов"""
        # Создаем несколько операторов с уникальными email
        for i in range(3):
            response = client.post(
                "/api/v1/operators/",
                json={
                    "name": f"Оператор {i}",
                    "email": f"operator{i}@test.com",
                    "max_load": 10,
                    "is_active": True,
                },
            )
            assert response.status_code == status.HTTP_200_OK

        response = client.get("/api/v1/operators/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 3

    def test_get_operator_by_id(self, client):
        """Тест получения оператора по ID"""
        # Создаем оператора с уникальным email
        create_response = client.post(
            "/api/v1/operators/",
            json={
                "name": "Тестовый Оператор для получения",
                "email": "get_operator@test.com",
                "max_load": 10,
                "is_active": True,
            },
        )

        if create_response.status_code != status.HTTP_200_OK:
            print(f"Error creating operator: {create_response.json()}")

        assert create_response.status_code == status.HTTP_200_OK
        operator_id = create_response.json()["id"]

        # Получаем оператора
        response = client.get(f"/api/v1/operators/{operator_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == operator_id
        assert data["name"] == "Тестовый Оператор для получения"

    def test_get_nonexistent_operator(self, client):
        """Тест получения несуществующего оператора"""
        response = client.get("/api/v1/operators/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_available_operators(self, client):
        """Тест получения доступных операторов"""
        # Создаем операторов с уникальными email
        operators = []

        # Активный оператор с нагрузкой
        op1_response = client.post(
            "/api/v1/operators/",
            json={
                "name": "Активный 1",
                "email": "active1_available@test.com",
                "max_load": 5,
                "is_active": True,
            },
        )
        assert op1_response.status_code == status.HTTP_200_OK
        operators.append(op1_response.json())

        # Неактивный оператор
        op2_response = client.post(
            "/api/v1/operators/",
            json={
                "name": "Неактивный",
                "email": "inactive_available@test.com",
                "max_load": 10,
                "is_active": False,
            },
        )
        assert op2_response.status_code == status.HTTP_200_OK
        operators.append(op2_response.json())

        # Активный оператор без нагрузки
        op3_response = client.post(
            "/api/v1/operators/",
            json={
                "name": "Активный 2",
                "email": "active2_available@test.com",
                "max_load": 10,
                "is_active": True,
            },
        )
        assert op3_response.status_code == status.HTTP_200_OK
        operators.append(op3_response.json())

        response = client.get("/api/v1/operators/available")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Проверяем, что только активные операторы в списке
        operator_names = [op["name"] for op in data]
        assert "Активный 1" in operator_names
        assert "Активный 2" in operator_names
        assert "Неактивный" not in operator_names

    def test_update_operator(self, client):
        """Тест обновления оператора"""
        # Создаем оператора с уникальным email
        create_response = client.post(
            "/api/v1/operators/",
            json={
                "name": "Оператор для обновления",
                "email": "update_operator@test.com",
                "max_load": 10,
                "is_active": True,
            },
        )

        if create_response.status_code != status.HTTP_200_OK:
            print(f"Error creating operator: {create_response.json()}")

        assert create_response.status_code == status.HTTP_200_OK
        operator_id = create_response.json()["id"]

        # Обновляем оператора
        update_data = {"name": "Обновленное Имя", "max_load": 20, "is_active": False}

        response = client.put(f"/api/v1/operators/{operator_id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["name"] == update_data["name"]
        assert data["max_load"] == update_data["max_load"]
        assert data["is_active"] == update_data["is_active"]

    def test_update_nonexistent_operator(self, client):
        """Тест обновления несуществующего оператора"""
        update_data = {"name": "Новое имя"}
        response = client.put("/api/v1/operators/999", json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_operator(self, client):
        """Тест удаления оператора"""
        # Создаем оператора с уникальным email
        create_response = client.post(
            "/api/v1/operators/",
            json={
                "name": "Оператор для удаления",
                "email": "delete_operator@test.com",
                "max_load": 10,
                "is_active": True,
            },
        )

        if create_response.status_code != status.HTTP_200_OK:
            print(f"Error creating operator: {create_response.json()}")

        assert create_response.status_code == status.HTTP_200_OK
        operator_id = create_response.json()["id"]

        # Удаляем оператора
        response = client.delete(f"/api/v1/operators/{operator_id}")

        assert response.status_code == status.HTTP_200_OK
        assert "deleted" in response.json()["message"].lower()

        # Проверяем, что оператор удален
        get_response = client.get(f"/api/v1/operators/{operator_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_operator(self, client):
        """Тест удаления несуществующего оператора"""
        response = client.delete("/api/v1/operators/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
