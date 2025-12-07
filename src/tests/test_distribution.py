from fastapi import status


class TestDistributionLogic:
    """Тесты для логики распределения"""

    def test_weight_based_distribution(self, client):
        """Тест распределения по весам"""
        # Создаем двух операторов с разными весами
        operators = []

        # Оператор 1 с весом 70
        op1_response = client.post(
            "/api/v1/operators/",
            json={
                "name": "Оператор 70%",
                "email": "op1_weight70@test.com",
                "max_load": 10,
                "is_active": True,
            },
        )
        assert op1_response.status_code == status.HTTP_200_OK
        operators.append(op1_response.json())

        # Оператор 2 с весом 30
        op2_response = client.post(
            "/api/v1/operators/",
            json={
                "name": "Оператор 30%",
                "email": "op2_weight30@test.com",
                "max_load": 10,
                "is_active": True,
            },
        )
        assert op2_response.status_code == status.HTTP_200_OK
        operators.append(op2_response.json())

        # Создаем источник
        source_response = client.post(
            "/api/v1/sources/",
            json={
                "name": "Тестовый Бот Распределение",
                "bot_token": "bot_token_distribution_123",
                "description": "Тестовый источник для распределения",
            },
        )
        assert source_response.status_code == status.HTTP_200_OK
        source_id = source_response.json()["id"]

        # Настраиваем веса
        client.post(
            f"/api/v1/sources/{source_id}/weights",
            json={"operator_id": operators[0]["id"], "weight": 70},
        )

        client.post(
            f"/api/v1/sources/{source_id}/weights",
            json={"operator_id": operators[1]["id"], "weight": 30},
        )

        # Создаем несколько контактов
        contact_counts = {operators[0]["id"]: 0, operators[1]["id"]: 0}
        total_contacts = 20  # Уменьшаем для скорости тестов

        for i in range(total_contacts):
            contact_data = {
                "lead_external_id": f"user_dist_{i}",
                "source_id": source_id,
                "message": f"Тестовое сообщение {i}",
            }

            response = client.post("/api/v1/contacts/", json=contact_data)
            assert response.status_code == status.HTTP_200_OK
            operator_id = response.json()["operator_id"]

            if operator_id in contact_counts:
                contact_counts[operator_id] += 1

        # Проверяем распределение (допускаем погрешность)
        total_assigned = sum(contact_counts.values())
        if total_assigned > 0:
            op1_percentage = contact_counts[operators[0]["id"]] / total_assigned * 100
            op2_percentage = contact_counts[operators[1]["id"]] / total_assigned * 100

            # Ожидаем примерно 70/30 распределение с большой погрешностью
            # для малого количества контактов
            assert 50 <= op1_percentage <= 90  # Допускаем большую погрешность
            assert 10 <= op2_percentage <= 50  # Допускаем большую погрешность

    def test_load_limit_respected(self, client):
        """Тест учета лимита нагрузки"""
        # Создаем оператора с маленьким лимитом
        op_response = client.post(
            "/api/v1/operators/",
            json={
                "name": "Оператор с лимитом 2",
                "email": "limited_op@test.com",
                "max_load": 2,  # Маленький лимит
                "is_active": True,
            },
        )
        assert op_response.status_code == status.HTTP_200_OK
        operator_id = op_response.json()["id"]

        # Создаем источник
        source_response = client.post(
            "/api/v1/sources/",
            json={
                "name": "Тестовый Бот Лимит",
                "bot_token": "bot_token_limit_123",
                "description": "Тестовый источник для теста лимита",
            },
        )
        assert source_response.status_code == status.HTTP_200_OK
        source_id = source_response.json()["id"]

        # Настраиваем вес
        client.post(
            f"/api/v1/sources/{source_id}/weights",
            json={"operator_id": operator_id, "weight": 100},
        )

        # Создаем контакты, превышающие лимит
        for i in range(4):  # 4 контакта при лимите 2
            contact_data = {
                "lead_external_id": f"user_limit_{i}",
                "source_id": source_id,
                "message": f"Тестовое сообщение {i}",
            }

            response = client.post("/api/v1/contacts/", json=contact_data)
            assert response.status_code == status.HTTP_200_OK

        # Проверяем нагрузку оператора
        operator_response = client.get(f"/api/v1/operators/{operator_id}")
        assert operator_response.status_code == status.HTTP_200_OK
        current_load = operator_response.json()["current_load"]

        # Оператор не должен превышать лимит
        assert current_load <= 2

    def test_inactive_operator_excluded(self, client):
        """Тест исключения неактивных операторов из распределения"""
        # Создаем активного и неактивного операторов
        operators = []

        # Активный оператор
        op1_response = client.post(
            "/api/v1/operators/",
            json={
                "name": "Активный",
                "email": "active_op@test.com",
                "max_load": 10,
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
                "email": "inactive_op@test.com",
                "max_load": 10,
                "is_active": False,
            },
        )
        assert op2_response.status_code == status.HTTP_200_OK
        operators.append(op2_response.json())

        # Создаем источник
        source_response = client.post(
            "/api/v1/sources/",
            json={
                "name": "Тестовый Бот Неактивный",
                "bot_token": "bot_token_inactive_123",
                "description": "Тестовый источник для теста неактивных",
            },
        )
        assert source_response.status_code == status.HTTP_200_OK
        source_id = source_response.json()["id"]

        # Настраиваем веса для обоих операторов
        client.post(
            f"/api/v1/sources/{source_id}/weights",
            json={"operator_id": operators[0]["id"], "weight": 50},
        )

        client.post(
            f"/api/v1/sources/{source_id}/weights",
            json={"operator_id": operators[1]["id"], "weight": 50},
        )

        # Создаем несколько контактов
        for i in range(5):  # Уменьшаем количество для скорости
            contact_data = {
                "lead_external_id": f"user_inactive_{i}",
                "source_id": source_id,
                "message": f"Тестовое сообщение {i}",
            }

            response = client.post("/api/v1/contacts/", json=contact_data)
            assert response.status_code == status.HTTP_200_OK
            operator_id = response.json()["operator_id"]

            # Все контакты должны быть назначены только активному оператору
            # или не назначены вообще
            assert operator_id is None or operator_id == operators[0]["id"]

    def test_lead_reuse(self, client):
        """Тест повторного использования лида"""
        # Создаем оператора
        operator_response = client.post(
            "/api/v1/operators/",
            json={
                "name": "Оператор для повторного использования",
                "email": "reuse_op@test.com",
                "max_load": 10,
                "is_active": True,
            },
        )
        assert operator_response.status_code == status.HTTP_200_OK
        operator_id = operator_response.json()["id"]

        # Создаем источник
        source_response = client.post(
            "/api/v1/sources/",
            json={
                "name": "Тестовый Бот Повтор",
                "bot_token": "bot_token_reuse_123",
                "description": "Тестовый источник для теста повторного использования",
            },
        )
        assert source_response.status_code == status.HTTP_200_OK
        source_id = source_response.json()["id"]

        # Настраиваем вес
        client.post(
            f"/api/v1/sources/{source_id}/weights",
            json={"operator_id": operator_id, "weight": 100},
        )

        external_id = f"reused_user_{source_id}"

        # Создаем несколько контактов от одного лида
        lead_ids = set()

        for i in range(3):
            contact_data = {
                "lead_external_id": external_id,
                "source_id": source_id,
                "message": f"Сообщение {i}",
            }

            response = client.post("/api/v1/contacts/", json=contact_data)
            assert response.status_code == status.HTTP_200_OK
            lead_ids.add(response.json()["lead_id"])

        # Все контакты должны ссылаться на одного лида
        assert len(lead_ids) == 1

        # Проверяем, что лид создан только один раз
        leads_response = client.get("/api/v1/leads/")
        assert leads_response.status_code == status.HTTP_200_OK

        user_leads = [
            lead for lead in leads_response.json() if lead["external_id"] == external_id
        ]

        assert len(user_leads) == 1
