from fastapi import status


class TestIntegration:
    """Интеграционные тесты полного цикла работы"""

    def test_complete_workflow(self, client):
        """Полный тестовый сценарий работы системы"""
        # 1. Создаем операторов
        operators = []

        for i in range(2):
            response = client.post(
                "/api/v1/operators/",
                json={
                    "name": f"Оператор {i + 1}",
                    "email": f"operator{i + 1}_workflow@test.com",
                    "max_load": 5,
                    "is_active": True,
                },
            )
            operators.append(response.json())

        # 2. Создаем источник
        source_response = client.post(
            "/api/v1/sources/",
            json={
                "name": "Workflow Bot",
                "bot_token": "workflow_bot_token",
                "description": "Бот для тестового workflow",
            },
        )
        source = source_response.json()

        # 3. Настраиваем распределение
        client.post(
            f"/api/v1/sources/{source['id']}/weights",
            json={"operator_id": operators[0]["id"], "weight": 60},
        )

        client.post(
            f"/api/v1/sources/{source['id']}/weights",
            json={"operator_id": operators[1]["id"], "weight": 40},
        )

        # 4. Создаем несколько обращений
        contacts = []

        for i in range(10):
            response = client.post(
                "/api/v1/contacts/",
                json={
                    "lead_external_id": f"workflow_user_{i}",
                    "source_id": source["id"],
                    "message": f"Запрос на услугу {i}",
                    "phone": f"+7916{i:08d}",
                    "full_name": f"Пользователь {i}",
                },
            )
            contacts.append(response.json())

        # 5. Проверяем распределение
        op1_contacts = [c for c in contacts if c["operator_id"] == operators[0]["id"]]
        op2_contacts = [c for c in contacts if c["operator_id"] == operators[1]["id"]]

        # Должны быть назначены все контакты (операторы не перегружены)
        assert len(op1_contacts) + len(op2_contacts) == 10

        # 6. Проверяем нагрузку операторов
        for i, operator in enumerate(operators):
            response = client.get(f"/api/v1/operators/{operator['id']}")
            operator_data = response.json()

            expected_load = len(op1_contacts) if i == 0 else len(op2_contacts)
            assert operator_data["current_load"] == expected_load

        # 7. Проверяем, что лиды созданы
        leads_response = client.get("/api/v1/leads/")
        assert len(leads_response.json()) == 10  # По одному лиду на каждый external_id

        # 8. Закрываем несколько контактов
        contacts_to_close = contacts[:3]

        for contact in contacts_to_close:
            response = client.put(f"/api/v1/contacts/{contact['id']}/close")
            assert response.status_code == status.HTTP_200_OK

        # 9. Проверяем, что нагрузка уменьшилась
        for i, operator in enumerate(operators):
            response = client.get(f"/api/v1/operators/{operator['id']}")
            operator_data = response.json()

            # Подсчитываем, сколько активных контактов осталось у оператора
            operator_contacts = op1_contacts if i == 0 else op2_contacts
            closed_count = sum(1 for c in contacts_to_close if c in operator_contacts)
            expected_load = len(operator_contacts) - closed_count

            assert operator_data["current_load"] == expected_load

        # 10. Создаем еще обращений (операторы теперь могут взять больше)
        new_contacts = []

        for i in range(3):
            response = client.post(
                "/api/v1/contacts/",
                json={
                    "lead_external_id": f"workflow_user_new_{i}",
                    "source_id": source["id"],
                    "message": f"Новый запрос {i}",
                },
            )
            new_contacts.append(response.json())

        # 11. Проверяем общую статистику
        all_contacts_response = client.get("/api/v1/contacts/")
        assert len(all_contacts_response.json()) == 13  # 10 + 3

        # 12. Проверяем контакты по операторам
        for operator in operators:
            response = client.get(f"/api/v1/contacts/by-operator/{operator['id']}")
            operator_contacts = response.json()

            # Проверяем, что все контакты имеют правильного оператора
            for contact in operator_contacts:
                assert contact["operator_id"] == operator["id"]

    def test_system_health(self, client):
        """Тест проверки здоровья системы"""
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self, client):
        """Тест корневого эндпоинта"""
        response = client.get("/")

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
