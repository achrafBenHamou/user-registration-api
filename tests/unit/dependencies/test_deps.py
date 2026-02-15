from unittest.mock import patch, MagicMock

from app.dependencies.deps import get_db_pool, get_user_service, get_user_repository
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


def test_get_db_pool():
    mock_pool = MagicMock()

    with patch("app.dependencies.deps.db_pool") as mock_db_pool:
        mock_db_pool.get_pool.return_value = mock_pool

        result = get_db_pool()

        assert result == mock_pool
        mock_db_pool.get_pool.assert_called_once()


def test_get_user_repository():
    mock_pool = MagicMock()

    repo = get_user_repository(pool=mock_pool)

    assert isinstance(repo, UserRepository)
    assert repo.pool == mock_pool


def test_get_user_service():
    mock_repo = MagicMock(spec=UserRepository)

    service = get_user_service(user_repository=mock_repo)

    assert isinstance(service, UserService)
    assert service.user_repository == mock_repo
