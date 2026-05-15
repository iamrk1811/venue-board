import pytest
from decimal import Decimal
from unittest.mock import MagicMock

from django.contrib.auth.models import User
from rest_framework.test import APIClient

from venues.models import Venue


@pytest.fixture
def venue(db):
    return Venue.objects.create(name="Taj Darbar", type=1, location="Mumbai")


@pytest.fixture
def user(db):
    return User.objects.create_user(username="arjun", password="testpass")


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def make_txn():
    def _make(venue_id, t, total, items=None):
        txn = MagicMock()
        txn.venue_id = venue_id
        txn.type = t
        txn.total = Decimal(str(total))
        mock_items = []
        for item_id, name, qty, price in (items or []):
            item = MagicMock()
            item.item_id = item_id
            item.name = name
            item.qty = qty
            item.price = Decimal(str(price))
            mock_items.append(item)
        txn.items.all.return_value = mock_items
        return txn

    return _make
