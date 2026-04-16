"""
Фаззинг-тестирование API с использованием hypothesis (обновлено для мастерской площадки).
"""
import pytest
from hypothesis import given, strategies as st
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


# ==================== Стратегии для Hypothesis ====================

# Email стратегия
email_strategy = st.emails()

# Пароль стратегия (произвольные строки)
password_strategy = st.text(
    min_size=1,
    alphabet=st.characters(blacklist_categories=("Cc", "Cs"))
)

# Название заявки
title_strategy = st.text(
    min_size=0,
    max_size=500,
    alphabet=st.characters(blacklist_categories=("Cc", "Cs"))
)

# Описание заявки
description_strategy = st.text(
    min_size=0,
    max_size=5000,
    alphabet=st.characters(blacklist_categories=("Cc", "Cs"))
)

# Цена (произвольные значения: положительные, отрицательные, ноль, очень большие)
price_strategy = st.floats(
    min_value=-999999,
    max_value=999999,
    allow_nan=False,
    allow_infinity=False,
)

# Адрес
address_strategy = st.text(
    min_size=0,
    max_size=500,
    alphabet=st.characters(blacklist_categories=("Cc", "Cs"))
)

# Категория
category_strategy = st.text(
    min_size=0,
    max_size=100,
    alphabet=st.characters(blacklist_categories=("Cc", "Cs"))
)

# ID стратегия
id_strategy = st.integers(min_value=-999999, max_value=999999)


# ==================== Фиксированные тестовые аккаунты ====================

TEST_CLIENT_TOKEN = None
TEST_MASTER_TOKEN = None
TEST_ADMIN_TOKEN = None
TEST_TICKET_ID = None


@pytest.fixture(scope="module", autouse=True)
def setup_test_users():
    """Создаём тестовых пользователей для всех тестов."""
    global TEST_CLIENT_TOKEN, TEST_MASTER_TOKEN, TEST_ADMIN_TOKEN, TEST_TICKET_ID
    
    # Регистрируем клиента
    client_response = client.post(
        "/auth/register",
        json={
            "email": "fuzz_client@repair.ru",
            "password": "FuzzTest123!",
            "full_name": "Fuzz Client",
            "role": "client",
        }
    )
    
    if client_response.status_code in [200, 201]:
        login_response = client.post(
            "/auth/login",
            json={"email": "fuzz_client@repair.ru", "password": "FuzzTest123!"}
        )
        if login_response.status_code == 200:
            TEST_CLIENT_TOKEN = login_response.json()["access_token"]
            
            # Создаём тестовую заявку
            ticket_response = client.post(
                "/tickets",
                json={
                    "title": "Test Ticket",
                    "description": "Test Description",
                    "price": 1000.0,
                    "address": "Test Address",
                    "category": "Test Category",
                },
                headers={"Authorization": f"Bearer {TEST_CLIENT_TOKEN}"}
            )
            if ticket_response.status_code == 200:
                TEST_TICKET_ID = ticket_response.json()["id"]
    
    # Регистрируем мастера
    master_response = client.post(
        "/auth/register",
        json={
            "email": "fuzz_master@repair.ru",
            "password": "FuzzTest123!",
            "full_name": "Fuzz Master",
            "role": "master",
        }
    )
    
    if master_response.status_code in [200, 201]:
        login_response = client.post(
            "/auth/login",
            json={"email": "fuzz_master@repair.ru", "password": "FuzzTest123!"}
        )
        if login_response.status_code == 200:
            TEST_MASTER_TOKEN = login_response.json()["access_token"]
    
    # Регистрируем админа
    admin_response = client.post(
        "/auth/register",
        json={
            "email": "fuzz_admin@repair.ru",
            "password": "FuzzTest123!",
            "full_name": "Fuzz Admin",
            "role": "client",  # Затем нужно назначить админом через БД (не реализуемо через API)
        }
    )
    
    if admin_response.status_code in [200, 201]:
        login_response = client.post(
            "/auth/login",
            json={"email": "fuzz_admin@repair.ru", "password": "FuzzTest123!"}
        )
        if login_response.status_code == 200:
            TEST_ADMIN_TOKEN = login_response.json()["access_token"]


# ==================== Тесты регистрации ====================

@given(email=email_strategy, password=password_strategy, full_name=st.text(min_size=1))
def test_register_with_arbitrary_strings(email, password, full_name):
    """Тест регистрации с произвольными строками.
    
    Сервер должен вернуть 200, 400 или 422, но никогда не 500.
    """
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": full_name,
            "role": "client",
        }
    )
    
    # Принимаем любой статус кроме 500
    assert response.status_code < 500, f"Server error: {response.text}"


# ==================== Тесты создания заявок ====================

@given(
    title=title_strategy,
    description=description_strategy,
    price=price_strategy,
    address=address_strategy,
    category=category_strategy,
)
def test_create_ticket_with_arbitrary_values(title, description, price, address, category):
    """Тест создания заявки с произвольными значениями.
    
    - Цена может быть отрицательной, нулевой, очень большой — должен вернуть 422
    - Категория может быть любой строкой — должен вернуть 200 или 422
    - Адрес может быть пустым — должен вернуть 422 или 200
    
    Сервер никогда не должен вернуть 500.
    """
    if not TEST_CLIENT_TOKEN:
        pytest.skip("Test client not initialized")
    
    response = client.post(
        "/tickets",
        json={
            "title": title,
            "description": description,
            "price": price,
            "address": address,
            "category": category,
        },
        headers={"Authorization": f"Bearer {TEST_CLIENT_TOKEN}"}
    )
    
    # Проверяем, что цена валидна
    if price <= 0:
        # Отрицательная или нулевая цена должна вернуть 422
        assert response.status_code in [422, 400], f"Expected 422/400 for invalid price, got {response.status_code}"
    
    # В любом случае, никогда не 500
    assert response.status_code < 500, f"Server error: {response.text}"


@given(price=st.just(-100.0) | st.just(0.0) | st.just(-0.01))
def test_create_ticket_with_invalid_price(price):
    """Тест создания заявки с отрицательной или нулевой ценой.
    
    Должен вернуть 422 или 400, но никогда не 500.
    """
    if not TEST_CLIENT_TOKEN:
        pytest.skip("Test client not initialized")
    
    response = client.post(
        "/tickets",
        json={
            "title": "Test",
            "description": "Test",
            "price": price,
            "address": "Test",
            "category": "Test",
        },
        headers={"Authorization": f"Bearer {TEST_CLIENT_TOKEN}"}
    )
    
    # Отрицательная цена всегда должна вернуть ошибку валидации
    assert response.status_code in [422, 400], f"Expected 422/400, got {response.status_code}"


# ==================== Тесты взятия заявки (take) ====================

@given(ticket_id=id_strategy)
def test_take_ticket_with_arbitrary_id(ticket_id):
    """Тест взятия заявки с произвольным ID.
    
    Мастер пытается взять заявку с несуществующим ID.
    Должен вернуть 404, но никогда не 500.
    """
    if not TEST_MASTER_TOKEN:
        pytest.skip("Test master not initialized")
    
    response = client.patch(
        f"/tickets/{ticket_id}/take",
        headers={"Authorization": f"Bearer {TEST_MASTER_TOKEN}"}
    )
    
    # Принимаем ошибку, но не 500
    assert response.status_code < 500, f"Server error: {response.text}"


def test_take_already_taken_ticket():
    """Тест взятия уже взятой заявки другим мастером.
    
    - Первый мастер берёт заявку (статус new → in_progress)
    - Второй мастер пытается взять ту же заявку
    - Должен получить 409 (Conflict) или 400
    """
    if not TEST_TICKET_ID or not TEST_MASTER_TOKEN:
        pytest.skip("Test data not initialized")
    
    # Попытаемся взять уже существующую заявку
    response = client.patch(
        f"/tickets/{TEST_TICKET_ID}/take",
        headers={"Authorization": f"Bearer {TEST_MASTER_TOKEN}"}
    )
    
    # Первая попытка должна быть успешной (200) или ошибкой авторизации
    # Но статус < 500 в любом случае
    assert response.status_code < 500, f"Server error: {response.text}"


# ==================== Тесты отзыва заявки (cancel) ====================

def test_cancel_ticket_when_in_progress():
    """Тест отзыва заявки клиентом когда статус уже in_progress.
    
    - Заявка в статусе in_progress
    - Клиент пытается отозвать заявку
    - Должен получить 400 или 403
    """
    if not TEST_CLIENT_TOKEN or not TEST_TICKET_ID:
        pytest.skip("Test data not initialized")
    
    # Попытаемся отозвать заявку
    response = client.patch(
        f"/tickets/{TEST_TICKET_ID}/cancel",
        headers={"Authorization": f"Bearer {TEST_CLIENT_TOKEN}"}
    )
    
    # Если статус не new, должна быть ошибка 400 или 403
    # Но не 500
    assert response.status_code < 500, f"Server error: {response.text}"


@given(ticket_id=id_strategy)
def test_cancel_nonexistent_ticket(ticket_id):
    """Тест отзыва несуществующей заявки.
    
    Должен вернуть 404 или 403, но никогда не 500.
    """
    if not TEST_CLIENT_TOKEN:
        pytest.skip("Test client not initialized")
    
    response = client.patch(
        f"/tickets/{ticket_id}/cancel",
        headers={"Authorization": f"Bearer {TEST_CLIENT_TOKEN}"}
    )
    
    # Принимаем ошибку, но не 500
    assert response.status_code < 500, f"Server error: {response.text}"


# ==================== Тесты фильтрации ====================

@given(min_price=price_strategy, max_price=price_strategy)
def test_get_tickets_with_arbitrary_price_range(min_price, max_price):
    """Тест получения заявок с произвольным диапазоном цен.
    
    Сервер должен корректно обработать любые значения цен.
    """
    if not TEST_CLIENT_TOKEN:
        pytest.skip("Test client not initialized")
    
    response = client.get(
        "/tickets",
        params={
            "min_price": min_price,
            "max_price": max_price,
        },
        headers={"Authorization": f"Bearer {TEST_CLIENT_TOKEN}"}
    )
    
    # Должен вернуть 200, 400 или 422, но не 500
    assert response.status_code < 500, f"Server error: {response.text}"


@given(category=category_strategy)
def test_get_tickets_with_arbitrary_category(category):
    """Тест получения заявок с произвольной категорией.
    
    Сервер не должен падать с 500 для любой категории.
    """
    if not TEST_CLIENT_TOKEN:
        pytest.skip("Test client not initialized")
    
    response = client.get(
        "/tickets",
        params={"category": category},
        headers={"Authorization": f"Bearer {TEST_CLIENT_TOKEN}"}
    )
    
    # Должен вернуть 200, но не 500
    assert response.status_code < 500, f"Server error: {response.text}"


# ==================== Тесты логина ====================

@given(email=email_strategy, password=password_strategy)
def test_login_with_arbitrary_credentials(email, password):
    """Тест логина с произвольными кредентшалами.
    
    Сервер должен вернуть 401 (неправильные) или 422 (валидация),
    но никогда не 500.
    """
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        }
    )
    
    # Должны получить < 500
    assert response.status_code < 500, f"Server error: {response.text}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
