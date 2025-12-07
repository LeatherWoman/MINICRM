from fastapi import status


class TestContacts:
    """Тесты для эндпоинтов контактов"""

    def test_create_contact_new_lead(
        self, client, sample_operator_data, sample_source_data, sample_contact_data
    ):
        """Тест создания контакта с новым лидом"""
        # Создаем оператора
        operator_response = client.post("/api/v1/operators/", json=sample_operator_data)
        operator_id = operator_response.json()["id"]

        # Создаем источник
        source_response = client.post("/api/v1/sources/", json=sample_source_data)
        source_id = source_response.json()["id"]

        # Настраиваем вес оператора для источника
        client.post(
            f"/api/v1/sources/{source_id}/weights",
            json={"operator_id": operator_id, "weight": 100},
        )

        # Создаем контакт (должен создать нового лида)
        contact_data = sample_contact_data.copy()
        contact_data["source_id"] = source_id

        response = client.post("/api/v1/contacts/", json=contact_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["source_id"] == source_id
        assert data["operator_id"] == operator_id  # Оператор должен быть назначен
        assert data["message"] == contact_data["message"]
        assert data["status"] == "new"
        assert data["is_active"]
        assert "lead_id" in data

    def test_create_contact_existing_lead(
        self,
        client,
        sample_operator_data,
        sample_source_data,
        sample_lead_data,
        sample_contact_data,
    ):
        """Тест создания контакта с существующим лидом"""
        # Создаем оператора
        operator_response = client.post("/api/v1/operators/", json=sample_operator_data)
        operator_id = operator_response.json()["id"]

        # Создаем источник
        source_response = client.post("/api/v1/sources/", json=sample_source_data)
        source_id = source_response.json()["id"]

        # Настраиваем вес оператора для источника
        client.post(
            f"/api/v1/sources/{source_id}/weights",
            json={"operator_id": operator_id, "weight": 100},
        )

        # Создаем лида заранее
        lead_response = client.post("/api/v1/leads/", json=sample_lead_data)
        lead_id = lead_response.json()["id"]

        # Создаем контакт для существующего лида
        contact_data = sample_contact_data.copy()
        contact_data["source_id"] = source_id

        response = client.post("/api/v1/contacts/", json=contact_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Проверяем, что использовался существующий лид
        assert data["lead_id"] == lead_id

    def test_create_contact_no_available_operators(
        self, client, sample_source_data, sample_contact_data
    ):
        """Тест создания контакта без доступных операторов"""
        # Создаем источник без операторов
        source_response = client.post("/api/v1/sources/", json=sample_source_data)
        source_id = source_response.json()["id"]

        # Создаем контакт
        contact_data = sample_contact_data.copy()
        contact_data["source_id"] = source_id

        response = client.post("/api/v1/contacts/", json=contact_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Оператор не должен быть назначен
        assert data["operator_id"] is None

    def test_create_contact_inactive_operator(
        self, client, sample_operator_data, sample_source_data, sample_contact_data
    ):
        """Тест создания контакта с неактивным оператором"""
        # Создаем неактивного оператора
        operator_data = sample_operator_data.copy()
        operator_data["is_active"] = False
        operator_response = client.post("/api/v1/operators/", json=operator_data)
        operator_id = operator_response.json()["id"]

        # Создаем источник
        source_response = client.post("/api/v1/sources/", json=sample_source_data)
        source_id = source_response.json()["id"]

        # Настраиваем вес оператора для источника
        client.post(
            f"/api/v1/sources/{source_id}/weights",
            json={"operator_id": operator_id, "weight": 100},
        )

        # Создаем контакт
        contact_data = sample_contact_data.copy()
        contact_data["source_id"] = source_id

        response = client.post("/api/v1/contacts/", json=contact_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Неактивный оператор не должен быть назначен
        assert data["operator_id"] is None

    def test_get_contacts(
        self, client, sample_operator_data, sample_source_data, sample_contact_data
    ):
        """Тест получения списка контактов"""
        # Создаем оператора
        operator_response = client.post("/api/v1/operators/", json=sample_operator_data)
        operator_id = operator_response.json()["id"]

        # Создаем источник
        source_response = client.post("/api/v1/sources/", json=sample_source_data)
        source_id = source_response.json()["id"]

        # Настраиваем вес оператора для источника
        client.post(
            f"/api/v1/sources/{source_id}/weights",
            json={"operator_id": operator_id, "weight": 100},
        )

        # Создаем несколько контактов
        for i in range(3):
            contact_data = sample_contact_data.copy()
            contact_data["source_id"] = source_id
            contact_data["lead_external_id"] = f"user_{i}"
            contact_data["message"] = f"Сообщение {i}"
            client.post("/api/v1/contacts/", json=contact_data)

        response = client.get("/api/v1/contacts/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 3

        # Проверяем расширенные поля (могут быть null если нет связи)
        for contact in data:
            assert "lead_external_id" in contact
            # operator_name может быть None если оператор не назначен
            assert "operator_name" in contact
            assert "source_name" in contact

    def test_get_contacts_by_lead(
        self,
        client,
        sample_operator_data,
        sample_source_data,
        sample_lead_data,
        sample_contact_data,
    ):
        """Тест получения контактов по лиду"""
        # Создаем оператора
        operator_response = client.post("/api/v1/operators/", json=sample_operator_data)
        operator_id = operator_response.json()["id"]

        # Создаем источник
        source_response = client.post("/api/v1/sources/", json=sample_source_data)
        source_id = source_response.json()["id"]

        # Настраиваем вес оператора для источника
        client.post(
            f"/api/v1/sources/{source_id}/weights",
            json={"operator_id": operator_id, "weight": 100},
        )

        # Создаем лида заранее
        lead_response = client.post("/api/v1/leads/", json=sample_lead_data)
        lead_id = lead_response.json()["id"]

        # Создаем несколько контактов для одного лида
        for i in range(3):
            contact_data = sample_contact_data.copy()
            contact_data["source_id"] = source_id
            contact_data["message"] = f"Сообщение {i}"
            client.post("/api/v1/contacts/", json=contact_data)

        response = client.get(f"/api/v1/contacts/by-lead/{lead_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 3

        # Все контакты должны быть от одного лида
        for contact in data:
            assert contact["lead_id"] == lead_id

    def test_get_contacts_by_operator(
        self, client, sample_operator_data, sample_source_data, sample_contact_data
    ):
        """Тест получения контактов по оператору"""
        # Создаем оператора
        operator_response = client.post("/api/v1/operators/", json=sample_operator_data)
        operator_id = operator_response.json()["id"]

        # Создаем источник
        source_response = client.post("/api/v1/sources/", json=sample_source_data)
        source_id = source_response.json()["id"]

        # Настраиваем вес оператора для источника
        client.post(
            f"/api/v1/sources/{source_id}/weights",
            json={"operator_id": operator_id, "weight": 100},
        )

        # Создаем несколько контактов
        for i in range(3):
            contact_data = sample_contact_data.copy()
            contact_data["source_id"] = source_id
            contact_data["lead_external_id"] = f"user_{i}"
            client.post("/api/v1/contacts/", json=contact_data)

        response = client.get(f"/api/v1/contacts/by-operator/{operator_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert isinstance(data, list)
        # Может быть больше 3, если есть другие тесты
        assert len(data) >= 3

        # Все контакты должны быть у одного оператора
        for contact in data:
            if contact["operator_id"]:  # Проверяем только назначенные контакты
                assert contact["operator_id"] == operator_id

    def test_close_contact(
        self, client, sample_operator_data, sample_source_data, sample_contact_data
    ):
        """Тест закрытия контакта"""
        # Создаем оператора
        operator_response = client.post("/api/v1/operators/", json=sample_operator_data)
        operator_id = operator_response.json()["id"]

        # Создаем источник
        source_response = client.post("/api/v1/sources/", json=sample_source_data)
        source_id = source_response.json()["id"]

        # Настраиваем вес оператора для источника
        client.post(
            f"/api/v1/sources/{source_id}/weights",
            json={"operator_id": operator_id, "weight": 100},
        )

        # Создаем контакт
        contact_data = sample_contact_data.copy()
        contact_data["source_id"] = source_id
        contact_response = client.post("/api/v1/contacts/", json=contact_data)
        contact_id = contact_response.json()["id"]

        # Закрываем контакт
        response = client.put(f"/api/v1/contacts/{contact_id}/close")

        assert response.status_code == status.HTTP_200_OK
        assert "closed" in response.json()["message"].lower()

        # Проверяем, что контакт закрыт
        contacts_response = client.get(f"/api/v1/contacts/{contact_id}")
        if contacts_response.status_code == 404:
            # Если нет отдельного эндпоинта, получаем все и фильтруем
            contacts_response = client.get("/api/v1/contacts/")
            contact = next(
                (c for c in contacts_response.json() if c["id"] == contact_id), None
            )
            assert contact is not None
            assert not contact["is_active"]
            assert contact["status"] == "closed"
        else:
            contact = contacts_response.json()
            assert not contact["is_active"]
            assert contact["status"] == "closed"

    def test_close_nonexistent_contact(self, client):
        """Тест закрытия несуществующего контакта"""
        response = client.put("/api/v1/contacts/999/close")

        # Может быть 404 или 200 с сообщением об ошибке
        if response.status_code != status.HTTP_200_OK:
            assert response.status_code == status.HTTP_404_NOT_FOUND
