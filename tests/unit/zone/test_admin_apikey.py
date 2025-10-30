import json
import pytest
from unittest.mock import patch
from collections import namedtuple
from typing import Dict, Any, Generator

import powerdnsadmin
from powerdnsadmin.models.setting import Setting
from powerdnsadmin.models.domain import Domain
from powerdnsadmin.models.api_key import ApiKey
from powerdnsadmin.models.role import Role
from powerdnsadmin.lib.validators import validate_zone
from powerdnsadmin.lib.schema import DomainSchema
from tests.conftest import admin_apikey_data, load_data


class TestUnitApiZoneAdminApiKey:
    @pytest.fixture
    def common_data_mock(self, app) -> Generator[None, None, None]:
        patchers = {}
        mocks = {}
        
        # Define all patchers
        patch_targets = {
            'google': 'powerdnsadmin.services.google.Setting',
            'github': 'powerdnsadmin.services.github.Setting',
            'azure': 'powerdnsadmin.services.azure.Setting',
            'oidc': 'powerdnsadmin.services.oidc.Setting',
            'helpers': 'powerdnsadmin.lib.helper.Setting',
            'models': 'powerdnsadmin.models.setting.Setting',
            'domain': 'powerdnsadmin.models.domain.Setting',
            'record': 'powerdnsadmin.models.record.Setting',
            'server': 'powerdnsadmin.models.server.Setting',
            'apikey': 'powerdnsadmin.decorators.ApiKey',
            'hist': 'powerdnsadmin.routes.api.History',
            'setting': 'powerdnsadmin.routes.api.Setting',
            'decorators': 'powerdnsadmin.decorators.Setting'
        }

        with app.app_context():
            # Create and start all patches
            for name, target in patch_targets.items():
                patchers[name] = patch(target)
                mocks[name] = patchers[name].start()
                if name != 'apikey' and name != 'hist':
                    mocks[name].return_value.get.side_effect = load_data

            # Configure API key mock
            data = admin_apikey_data()
            api_key = ApiKey(
                desc=data['description'],
                role_name=data['role'],
                domains=[]
            )
            api_key.role = Role(name=data['role'])
            mocks['apikey'].return_value.is_validate.return_value = api_key

            yield mocks

            # Stop all patches
            for patcher in patchers.values():
                patcher.stop()


    def test_empty_get(self, client, common_data_mock, admin_apikey):
        with patch('powerdnsadmin.routes.api.Domain') as mock_domain, \
             patch('powerdnsadmin.lib.utils.requests.get') as mock_get:
            mock_domain.return_value.domains.return_value = []
            mock_domain.query.all.return_value = []
            mock_get.return_value.json.return_value = []
            mock_get.return_value.status_code = 200

            res = client.get("/api/v1/servers/pdnsadmin/zones",
                             headers=admin_apikey)

            data = res.get_json(force=True)
            assert res.status_code == 200
            assert data == []

    def test_create_zone(self, client, common_data_mock, zone_data,
                         admin_apikey, created_zone_data):
        with patch('powerdnsadmin.lib.helper.requests.request') as mock_post, \
             patch('powerdnsadmin.routes.api.Domain') as mock_domain:
            mock_post.return_value.status_code = 201
            mock_post.return_value.content = json.dumps(created_zone_data)
            mock_post.return_value.headers = {}
            mock_domain.return_value.update.return_value = True

            res = client.post("/api/v1/servers/localhost/zones",
                              headers=admin_apikey,
                              data=json.dumps(zone_data),
                              content_type="application/json")
            data = res.get_json(force=True)
            data['rrsets'] = []

            validate_zone(data)
            assert res.status_code == 201

    def test_get_multiple_zones(self, client, common_data_mock, zone_data,
                                admin_apikey):
        with patch('powerdnsadmin.routes.api.Domain') as mock_domain:
            test_domain = Domain(1, name=zone_data['name'].rstrip("."))
            mock_domain.query.all.return_value = [test_domain]

            res = client.get("/api/v1/servers/pdnsadmin/zones",
                             headers=admin_apikey)
            data = res.get_json(force=True)

            fake_domain = namedtuple("Domain",
                                     data[0].keys())(*data[0].values())
            domain_schema = DomainSchema(many=True)

            json.dumps(domain_schema.dump([fake_domain]))
            assert res.status_code == 200

    def test_delete_zone(self, client, common_data_mock, zone_data,
                         admin_apikey):
        with patch('powerdnsadmin.lib.utils.requests.request') as mock_delete, \
             patch('powerdnsadmin.routes.api.Domain') as mock_domain:
            mock_domain.return_value.update.return_value = True
            mock_delete.return_value.status_code = 204
            mock_delete.return_value.content = ''

            zone_url_format = "/api/v1/servers/localhost/zones/{0}"
            zone_url = zone_url_format.format(zone_data['name'].rstrip("."))
            res = client.delete(zone_url, headers=admin_apikey)

            assert res.status_code == 204
