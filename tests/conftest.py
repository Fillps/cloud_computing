import os
import pytest


from cloud_computing import create_app

@pytest.fixture
def app():
    app = create_app()
    return app



