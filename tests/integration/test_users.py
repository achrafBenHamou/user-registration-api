"""
Integration tests for user endpoints.

Tests the full flow of user registration, activation code request,
and account activation through the API endpoints.
"""

import base64
import pytest
from httpx import AsyncClient

from app.db.pool import db_pool


class TestUserRegistration:
    """Test cases for user registration endpoint."""

    @pytest.mark.asyncio
    async def test_register_user_success(self, client: AsyncClient, clean_database):
        """Test successful user registration."""
        payload = {"email": "test@example.com", "password": "SecurePass123"}

        response = await client.post("/api/v1/users/register", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["is_active"] is False
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(
        self, client: AsyncClient, clean_database
    ):
        """Test registration with an already registered email."""
        payload = {"email": "duplicate@example.com", "password": "SecurePass123"}

        response = await client.post("/api/v1/users/register", json=payload)
        assert response.status_code == 201

        response = await client.post("/api/v1/users/register", json=payload)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_user_invalid_email(
        self, client: AsyncClient, clean_database
    ):
        """Test registration with invalid email format."""
        payload = {"email": "invalid-email", "password": "SecurePass123"}

        response = await client.post("/api/v1/users/register", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_user_short_password(
        self, client: AsyncClient, clean_database
    ):
        """Test registration with password too short."""
        payload = {"email": "test@example.com", "password": "short"}

        response = await client.post("/api/v1/users/register", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_user_missing_fields(
        self, client: AsyncClient, clean_database
    ):
        """Test registration with missing required fields."""
        response = await client.post(
            "/api/v1/users/register", json={"email": "test@example.com"}
        )
        assert response.status_code == 422

        response = await client.post(
            "/api/v1/users/register", json={"password": "SecurePass123"}
        )
        assert response.status_code == 422

        response = await client.post("/api/v1/users/register", json={})
        assert response.status_code == 422


class TestActivationCodeRequest:
    """Test cases for activation code request endpoint."""

    def _get_basic_auth_header(self, email: str, password: str) -> dict:
        """Generate Basic Auth header."""
        credentials = f"{email}:{password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}

    @pytest.mark.asyncio
    async def test_request_activation_code_success(
        self, client: AsyncClient, clean_database
    ):
        """Test successful activation code request."""
        email = "test@example.com"
        password = "SecurePass123"
        await client.post(
            "/api/v1/users/register", json={"email": email, "password": password}
        )

        headers = self._get_basic_auth_header(email, password)
        response = await client.post("/api/v1/users/activation-code", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    @pytest.mark.asyncio
    async def test_request_activation_code_invalid_credentials(
        self, client: AsyncClient, clean_database
    ):
        """Test activation code request with invalid credentials."""
        email = "test@example.com"
        password = "SecurePass123"
        await client.post(
            "/api/v1/users/register", json={"email": email, "password": password}
        )

        headers = self._get_basic_auth_header(email, "WrongPassword")
        response = await client.post("/api/v1/users/activation-code", headers=headers)

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_request_activation_code_nonexistent_user(
        self, client: AsyncClient, clean_database
    ):
        """Test activation code request for non-existent user."""
        headers = self._get_basic_auth_header(
            "nonexistent@example.com", "SomePassword123"
        )
        response = await client.post("/api/v1/users/activation-code", headers=headers)

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_request_activation_code_no_auth(
        self, client: AsyncClient, clean_database
    ):
        """Test activation code request without authentication."""
        response = await client.post("/api/v1/users/activation-code")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_request_activation_code_already_activated(
        self, client: AsyncClient, clean_database
    ):
        """Test activation code request for already activated user."""
        email = "test@example.com"
        password = "SecurePass123"
        await client.post(
            "/api/v1/users/register", json={"email": email, "password": password}
        )

        async with db_pool.get_pool().acquire() as conn:
            await conn.execute(
                "UPDATE users SET is_active = TRUE WHERE email = $1", email
            )

        headers = self._get_basic_auth_header(email, password)
        response = await client.post("/api/v1/users/activation-code", headers=headers)

        assert response.status_code == 400
        assert "already activated" in response.json()["detail"].lower()


class TestUserActivation:
    """Test cases for user activation endpoint."""

    def _get_basic_auth_header(self, email: str, password: str) -> dict:
        """Generate Basic Auth header."""
        credentials = f"{email}:{password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}

    @pytest.mark.asyncio
    async def test_activate_user_success(self, client: AsyncClient, clean_database):
        """Test successful user activation with valid code."""
        email = "test@example.com"
        password = "SecurePass123"
        response = await client.post(
            "/api/v1/users/register", json={"email": email, "password": password}
        )
        user_id = response.json()["id"]

        test_code = "1234"
        async with db_pool.get_pool().acquire() as conn:
            # Delete auto-generated activation code first
            await conn.execute(
                "DELETE FROM activation_codes WHERE user_id = $1", user_id
            )
            await conn.execute(
                """
                INSERT INTO activation_codes (user_id, code, expires_at)
                VALUES ($1, $2, NOW() + INTERVAL '1 minute')
                """,
                user_id,
                test_code,
            )

        headers = self._get_basic_auth_header(email, password)
        response = await client.post(
            "/api/v1/users/activate", json={"code": test_code}, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "activated successfully" in data["message"].lower()

        async with db_pool.get_pool().acquire() as conn:
            result = await conn.fetchrow(
                "SELECT is_active FROM users WHERE email = $1", email
            )
            assert result["is_active"] is True

    @pytest.mark.asyncio
    async def test_activate_user_invalid_code(
        self, client: AsyncClient, clean_database
    ):
        """Test user activation with invalid code."""
        email = "test@example.com"
        password = "SecurePass123"
        response = await client.post(
            "/api/v1/users/register", json={"email": email, "password": password}
        )
        user_id = response.json()["id"]

        async with db_pool.get_pool().acquire() as conn:
            # Delete auto-generated activation code first
            await conn.execute(
                "DELETE FROM activation_codes WHERE user_id = $1", user_id
            )
            await conn.execute(
                """
                INSERT INTO activation_codes (user_id, code, expires_at)
                VALUES ($1, $2, NOW() + INTERVAL '1 minute')
                """,
                user_id,
                "1234",
            )

        headers = self._get_basic_auth_header(email, password)
        response = await client.post(
            "/api/v1/users/activate", json={"code": "9999"}, headers=headers
        )

        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_activate_user_expired_code(
        self, client: AsyncClient, clean_database
    ):
        """Test user activation with expired code."""
        email = "test@example.com"
        password = "SecurePass123"
        response = await client.post(
            "/api/v1/users/register", json={"email": email, "password": password}
        )
        user_id = response.json()["id"]

        test_code = "1234"
        async with db_pool.get_pool().acquire() as conn:
            # Delete auto-generated activation code first
            await conn.execute(
                "DELETE FROM activation_codes WHERE user_id = $1", user_id
            )
            # Insert code with created_at in the past and expires_at also in the past
            await conn.execute(
                """
                INSERT INTO activation_codes (user_id, code, created_at, expires_at)
                VALUES ($1, $2, NOW() - INTERVAL '2 minutes', NOW() - INTERVAL '1 minute')
                """,
                user_id,
                test_code,
            )

        headers = self._get_basic_auth_header(email, password)
        response = await client.post(
            "/api/v1/users/activate", json={"code": test_code}, headers=headers
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_activate_user_invalid_code_format(
        self, client: AsyncClient, clean_database
    ):
        """Test activation with invalid code format."""
        email = "test@example.com"
        password = "SecurePass123"
        await client.post(
            "/api/v1/users/register", json={"email": email, "password": password}
        )

        headers = self._get_basic_auth_header(email, password)

        response = await client.post(
            "/api/v1/users/activate", json={"code": "abcd"}, headers=headers
        )
        assert response.status_code == 422

        response = await client.post(
            "/api/v1/users/activate", json={"code": "123"}, headers=headers
        )
        assert response.status_code == 422

        response = await client.post(
            "/api/v1/users/activate", json={"code": "12345"}, headers=headers
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_activate_user_already_activated(
        self, client: AsyncClient, clean_database
    ):
        """Test activation of already activated user."""
        email = "test@example.com"
        password = "SecurePass123"
        response = await client.post(
            "/api/v1/users/register", json={"email": email, "password": password}
        )
        user_id = response.json()["id"]

        async with db_pool.get_pool().acquire() as conn:
            await conn.execute(
                "UPDATE users SET is_active = TRUE WHERE email = $1", email
            )

        test_code = "1234"
        async with db_pool.get_pool().acquire() as conn:
            # Delete auto-generated activation code first
            await conn.execute(
                "DELETE FROM activation_codes WHERE user_id = $1", user_id
            )
            await conn.execute(
                """
                INSERT INTO activation_codes (user_id, code, expires_at)
                VALUES ($1, $2, NOW() + INTERVAL '1 minute')
                """,
                user_id,
                test_code,
            )

        headers = self._get_basic_auth_header(email, password)
        response = await client.post(
            "/api/v1/users/activate", json={"code": test_code}, headers=headers
        )

        assert response.status_code == 400
        assert "already activated" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_activate_user_no_auth(self, client: AsyncClient, clean_database):
        """Test activation without authentication."""
        response = await client.post("/api/v1/users/activate", json={"code": "1234"})

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_activate_user_wrong_credentials(
        self, client: AsyncClient, clean_database
    ):
        """Test activation with wrong credentials."""
        email = "test@example.com"
        password = "SecurePass123"
        await client.post(
            "/api/v1/users/register", json={"email": email, "password": password}
        )

        headers = self._get_basic_auth_header(email, "WrongPassword")
        response = await client.post(
            "/api/v1/users/activate", json={"code": "1234"}, headers=headers
        )

        assert response.status_code == 401


class TestUserFlowIntegration:
    """Test complete user registration and activation flow."""

    def _get_basic_auth_header(self, email: str, password: str) -> dict:
        """Generate Basic Auth header."""
        credentials = f"{email}:{password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}

    @pytest.mark.asyncio
    async def test_complete_user_flow(self, client: AsyncClient, clean_database):
        """Test complete flow: register -> request code -> activate."""
        email = "flow@example.com"
        password = "SecurePass123"

        response = await client.post(
            "/api/v1/users/register", json={"email": email, "password": password}
        )
        assert response.status_code == 201
        user_data = response.json()
        assert user_data["is_active"] is False

        headers = self._get_basic_auth_header(email, password)
        response = await client.post("/api/v1/users/activation-code", headers=headers)
        assert response.status_code == 200

        async with db_pool.get_pool().acquire() as conn:
            code_data = await conn.fetchrow(
                """
                SELECT code FROM activation_codes 
                WHERE user_id = $1 AND expires_at > NOW()
                ORDER BY created_at DESC
                LIMIT 1
                """,
                user_data["id"],
            )

        assert code_data is not None
        activation_code = code_data["code"]

        response = await client.post(
            "/api/v1/users/activate", json={"code": activation_code}, headers=headers
        )
        assert response.status_code == 200

        async with db_pool.get_pool().acquire() as conn:
            user = await conn.fetchrow(
                "SELECT is_active FROM users WHERE email = $1", email
            )
            assert user["is_active"] is True
