# -*- coding: utf-8 -*-

import pytest


@pytest.mark.parametrize('url, status_code', [
    ('/',  200),
    ('/{item_name}',  200),
])
def test_api_request(url, status_code, test_client, api_url_data):
    url_str = url.format(item_name=api_url_data['single_item_name'])
    res = test_client.get(url_str)
    assert res.status_code == status_code
