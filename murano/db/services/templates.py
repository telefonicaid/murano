# Copyright (c) 2015 Telefonica I+D.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from murano.common import uuidutils
from murano.db import models

from murano.db import session as db_session


class TemplateServices(object):
    @staticmethod
    def get_templates_by(filters):
        """Returns list of environments
           :param filters: property filters
           :return: Returns list of environments
        """
        unit = db_session.get_session()
        templates = unit.query(models.Template). \
            filter_by(**filters).all()

        return templates

    @staticmethod
    def create(template_params, tenant_id):
        #tagging environment by tenant_id for later checks
        """Creates template with specified params, in particular - name

           :param template_params: Dict, e.g. {'name': 'temp-name'}
           :param tenant_id: Tenant Id
           :return: Created Template
        """

        template_params['id'] = uuidutils.generate_uuid()
        template_params['tenant_id'] = tenant_id
        template = models.Template()
        template.update(template_params)

        unit = db_session.get_session()
        with unit.begin():
            unit.add(template)

        #saving environment as Json to itself
        template.update({'description': template_params})
        template.save(unit)

        return template

    @staticmethod
    def delete(template_id):
        """Deletes template

           :param template_id: Template that is going to be deleted
           :param token: OpenStack auth token
        """

        temp_description = TemplateServices.get_template_description(
            template_id, False)
        temp_description['description'] = None
        TemplateServices.save_template_description(
            temp_description, template_id)

    @staticmethod
    def remove(template_id):
        """It deletes the template from database.
           :param template_id: Template Id to be deleted.
        """
        unit = db_session.get_session()
        template = unit.query(models.Template).get(template_id)
        if template:
            with unit.begin():
                unit.delete(template)

    @staticmethod
    def update(template_id, body):
        """It updates the description of a template.
           :param template_id: Template Id to be deleted.
           :param body: The description to be updated.
           :return the template description updated
        """
        unit = db_session.get_session()
        template = unit.query(models.Template).get(template_id)
        template.update(body)
        template.save(unit)
        return template

    @staticmethod
    def get_template_description(template_id, inner=True):
        """Returns template description for specified template.

           :param template_id: Template Id
           :param inner: return contents of template rather than whole
            Object Model structure
           :return: Template Description Object
        """
        unit = db_session.get_session()

        temp = (unit.query(models.Template).get(template_id))

        if temp is None:
            raise ValueError("The template does not exists")

        return temp.description

    @staticmethod
    def get_application_description(template_id, application_id, inner=True):
        """Returns template description for specified template.

           :param template_id: Template Id
           :param inner: return contents of template rather than whole
            Object Model structure
           :return: Template Description Object
        """
        unit = db_session.get_session()

        temp = (unit.query(models.Template).get(template_id))
        temp_description = temp.description

        if not "services" in temp_description:
            return []
        else:
            return temp_description['services']

    @staticmethod
    def save_template_description(template_des, template_id=None):
        """Saves template description to specified session.

           :param template_des: Template Description
           :param template_id: The template ID.
        """
        unit = db_session.get_session()
        template = unit.query(models.Template).get(template_id)
        template.update({'description': template_des})
        template.save(unit)

    @staticmethod
    def template_exist(template_id):
        """It checks if the template exits in database

           :param template_id: The template ID
           :param inner: save modifications to only content of environment
            rather than whole Object Model structure
        """
        session = db_session.get_session()
        template = session.query(models.Template).get(template_id)

        if template is None:
            return False
        else:
            return True

    @staticmethod
    def get_template(template_id):
        """It obtains the template information from the database.
           :param template_id: The template ID
        """
        session = db_session.get_session()
        return session.query(models.Template).get(template_id)

    @staticmethod
    def create_environment(environment_id, token):
        pass
