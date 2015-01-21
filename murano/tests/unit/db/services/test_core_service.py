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
from murano.db.services import core_services
from murano.tests.unit import base


def get_template_empty_mock():
    return {
        "tenant_id": "tenant_id",
        "name": "henar",
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
                "id": "tomcat_id"
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
        "tenant_id": "tenant_id",
        "name": "template_name",
        'id': 'template_id',
        "?": {
            "type": "io.murano.Template",
            "id": "temp_object_id"}
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
                "id": "tomcat_id"
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
            "id": "tomcat_id"
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


class TestCoreServices(base.MuranoTestCase):
    def setUp(self):
        super(TestCoreServices, self).setUp()
        self.core_services = core_services.CoreServices

    @mock.patch('murano.db.services.templates.TemplateServices')
    def test_empty_template(self, template_services_mock):
        """Check obtaining the template description without services."""
        template_services_mock.get_template_description.return_value = \
            get_template_empty_mock()
        template_des = self.core_services.get_template_data('any', '/services')
        self.assertEqual(template_des, [])

    @mock.patch('murano.db.services.templates.TemplateServices')
    def test_template_services(self, template_services_mock):
        """Check obtaining the template description with services."""
        template_services_mock.get_template_description.return_value = \
            get_template_services_mock()
        template_des = self.core_services.get_template_data('any', '/services')
        self.assertEqual(template_des, get_services())

    @mock.patch('murano.db.services.templates.TemplateServices')
    def test_template_get_service(self, template_services_mock):
        """Check obtaining the service description"""
        template_services_mock.get_template_description.return_value = \
            get_template_services_mock()
        template_des = self.core_services.get_template_data('any',
            '/services/tomcat_id')
        self.assertEqual(template_des, get_service_tomcat())

    @mock.patch('murano.db.services.templates.TemplateServices')
    def test_template_post_services(self, template_services_mock):
        """Check adding a service to a template"""
        template_services_mock.get_template_description.return_value = \
            get_template_empty_mock()
        template_des = self.core_services.post_template_data('any',
            get_services(), '/services')
        self.assertEqual(template_des, get_services())

    @mock.patch('murano.db.services.templates.TemplateServices')
    def test_template_delete_services(self, template_services_mock):
        """Check deleting a service in a template"""
        template_services_mock.get_template_description.return_value = \
            get_template_services_mock()
        self.core_services.delete_template_data('any',
            '/services/54aaa43d-5970-4c73-b9ac-fea656f3c722')
        template_des = self.core_services.get_template_data('any', '/services')
        self.assertEqual(template_des, [get_service_tomcat()])

    @mock.patch('murano.db.services.templates.TemplateServices')
    def test_get_template_no_exists(self, template_services_mock):
        """Check obtaining a non-existing service """
        template_services_mock.get_template_description.return_value = \
            get_template_services_mock()
        self.assertRaises(ValueError,
            self.core_services.get_template_data, 'any', '/services/noexists')

    @mock.patch('murano.db.services.templates.TemplateServices')
    def test_adding_services(self, template_services_mock):
        """Check adding services to a template"""
        template_services_mock.get_template_description.return_value =\
            get_template_empty_mock()
        self.core_services.post_template_data('any',
            get_service_tomcat(), '/services')
        self.core_services.post_template_data('any',
            get_service_mysql(), '/services')
        template_des = \
            self.core_services.get_template_data('any', '/services')
        self.assertEqual(template_des, get_services())
