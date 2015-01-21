# Copyright (c) 2015 Telefonica I+D.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock

from murano.db.services import templates as templates
from murano.tests.unit import base


def get_template_empty_mock():
    return {
        "tenant_id": "tenand_id",
        "name": "mytemplate",
        'id': 'template_id',
        "?": {
            "type": "io.murano.Template",
            "id": "temp_object_id"
        }
    }


def get_template_services_mock():
    template = {
        "services": [
        {
            "instance": {
                "assignFloatingIp": "true",
                "keyname": "mykeyname",
                "image": "cloud-fedora-v3",
                "flavor": "m1.medium",
                "?": {
                    "type": "io.murano.resources.LinuxMuranoInstance",
                    "id": "ef984a74-29a4-45c0-b1dc-2ab9f075732e"
                }
            },
            "name": "orion",
            "?":
            {
                "_26411a1861294160833743e45d0eaad9": {
                    "name": "tomcat"
                },
                "type": "io.murano.apps.apache.Tomcat",
                "id": "54cea43d-5970-4c73-b9ac-fea656f3c722"
            },
            "port": "8080"
        }, {
            "instance": "ef984a74-29a4-45c0-b1dc-2ab9f075732e",
            "password": "XXX", "name":
            "mysql",
            "?": {
                "_26411a1861294160833743e45d0eaad9": {
                    "name": "mysql"
                },
                "type": "io.murano.apps.database.MySQL",
                "id": "54aaa43d-5970-4c73-b9ac-fea656f3c722"
            }
        }
        ],
        "tenant_id": "tenand_id",
        "name": "mytemplate",
        'id': 'template_id',
        "?": {
            "type": "io.murano.Template",
            "id": "temp_object_id"
        }
    }
    return template


def get_services():
    return [
        {
            "instance": {
                "assignFloatingIp": "true",
                "keyname": "mykeyname",
                "image": "cloud-fedora-v3",
                "flavor": "m1.medium",
                "?": {
                    "type": "io.murano.resources.LinuxMuranoInstance",
                    "id": "ef984a74-29a4-45c0-b1dc-2ab9f075732e"
                }
            },
            "name": "orion",
            "?":
            {
                "_26411a1861294160833743e45d0eaad9": {
                    "name": "tomcat"
                },
                "type": "io.murano.apps.apache.Tomcat",
                "id": "54cea43d-5970-4c73-b9ac-fea656f3c722"
            },
            "port": "8080"
        },
        {
            "instance": "ef984a74-29a4-45c0-b1dc-2ab9f075732e",
            "password": "XXX", "name":
            "mysql",
            "?": {
                "_26411a1861294160833743e45d0eaad9": {
                    "name": "mysql"
                },
                "type": "io.murano.apps.database.MySQL",
                "id": "54aaa43d-5970-4c73-b9ac-fea656f3c722"
            }
        }
    ]


def get_service_tomcat():
    return {
        "instance": {
            "assignFloatingIp": "true",
            "keyname": "mykeyname",
            "image": "cloud-fedora-v3",
            "flavor": "m1.medium",
            "?": {
                "type": "io.murano.resources.LinuxMuranoInstance",
                "id": "ef984a74-29a4-45c0-b1dc-2ab9f075732e"
            }
        },
        "name": "orion",
        "?":
        {
            "_26411a1861294160833743e45d0eaad9": {
                "name": "tomcat"
            },
            "type": "io.murano.apps.apache.Tomcat",
            "id": "54cea43d-5970-4c73-b9ac-fea656f3c722"
        },
        "port": "8080"
    }


def get_service_mysql():
    return {
        "instance": "ef984a74-29a4-45c0-b1dc-2ab9f075732e",
        "password": "XXX", "name":
        "mysql",
        "?": {
            "_26411a1861294160833743e45d0eaad9": {
                "name": "mysql"
            },
            "type": "io.murano.apps.database.MySQL",
            "id": "54aaa43d-5970-4c73-b9ac-fea656f3c722"
        }
    }


class TestTemplateServices(base.MuranoWithDBTestCase):

    def setUp(self):
        super(TestTemplateServices, self).setUp()
        self.template_services = templates.TemplateServices

    def test_create_template(self):
        """Check the creation of a template."""
        body = {
            "name": "mytemplate"
        }
        uuids = ('temp_object_id', 'template_id')
        mock_uuid = self._stub_uuid(uuids)
        template_des = self.template_services.create(body, 'tenand_id')
        self.assertEqual(template_des.description, get_template_empty_mock())
        self.assertEqual(2, mock_uuid.call_count)

    def test_get_empty_template(self):
        """Check obtaining information about a template without services."""
        self.test_create_template()
        template = \
            self.template_services.get_template_description("template_id")
        self.assertEqual(template, get_template_empty_mock())

    def test_get_template_services(self):
        """Check obtaining information about a template with services."""
        uuids = ('temp_object_id', 'template_id')
        mock_uuid = self._stub_uuid(uuids)
        template = self.template_services.create(get_template_services_mock(),
                                                 'tenand_id')
        self.assertEqual(template.description, get_template_services_mock())
        self.assertEqual(2, mock_uuid.call_count)

        template_des = \
            self.template_services.get_template_description("template_id")
        self.assertEqual(template_des, get_template_services_mock())

    def test_get_template_no_exists(self):
        """Check obtaining information about a template which
        does not exist.
        """
        self.assertRaises(ValueError,
            self.template_services.get_template_description, 'no_exists')

    def test_delete_template(self):
        """Check deleting a template."""
        self.test_create_template()
        self.template_services.delete("template_id")

    def _stub_uuid(self, values=[]):
        class FakeUUID:
            def __init__(self, v):
                self.hex = v

        mock_uuid4 = mock.patch('uuid.uuid4').start()
        mock_uuid4.side_effect = [FakeUUID(v) for v in values]
        return mock_uuid4