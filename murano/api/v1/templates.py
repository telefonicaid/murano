#    Copyright (c) 2015, Telefonica I+D.
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

import re

from oslo.db import exception as db_exc
from webob import exc

from murano.api.v1 import request_statistics
from murano.common import policy
from murano.common import wsgi
from murano.db.services import core_services
from murano.db.services import templates as templates
from murano.openstack.common.gettextutils import _
from murano.openstack.common import log as logging

LOG = logging.getLogger(__name__)

API_NAME = 'Templates'

VALID_NAME_REGEX = re.compile('^[a-zA-Z]+[\w-]*$')


class Controller(object):
    @request_statistics.stats_count(API_NAME, 'Index')
    def index(self, request):
        """It lists the templates associated to an tenant-id.
        :param request: The operation request.
        :return: the template description list.
        """
        LOG.debug('Templates:List')
        policy.check('list_templates', request.context)

        #Only templates from same tenant as user should be returned
        filters = {'tenant_id': request.context.tenant}
        list_templates = templates.TemplateServices.get_templates_by(filters)
        list_templates = [temp.to_dict() for temp in list_templates]

        return {"templates": list_templates}

    @request_statistics.stats_count(API_NAME, 'Create')
    def create(self, request, body):
        """It creates the template from the payload obtaining.
        This payload can contain just the template name, or include
        also service information.
        :param request: the operation request.
        :param body: the template description
        :return: the description of the created template.
        """
        LOG.debug('Templates:Create <Body {0}>'.format(body))
        policy.check('create_template', request.context)
        #Validation
        try:
            LOG.debug('TEMP NAME: {0}>'.format(body['name']))
            if not VALID_NAME_REGEX.match(str(body['name'])):
                msg = _('Template must contain only alphanumeric '
                    'or "_-." characters, must start with alpha')
                LOG.exception(msg)
                raise exc.HTTPClientError(msg)
        except Exception:
                msg = _('Template body is incorrect')
                LOG.exception(msg)
                raise exc.HTTPClientError(msg)
        try:
            template = templates.TemplateServices.create(
                body.copy(), request.context.tenant)
            return template.to_dict()
        except db_exc.DBDuplicateEntry:
            msg = _('Template with specified name already exists')
            LOG.exception(msg)
            raise exc.HTTPConflict(msg)

    @request_statistics.stats_count(API_NAME, 'Show')
    def show(self, request, template_id):
        """It shows the description about a template.
        :param request: the operation request.
        :param template_id: the template ID.
        :return: the description of the template.
        """
        LOG.debug('Templates:Show <Id: {0}>'.format(template_id))
        target = {"template_id": template_id}
        policy.check('show_template', request.context, target)

        self._validate_request(request, template_id)

        template = templates.TemplateServices.get_template(template_id)
        temp = template.to_dict()

        #add services to template
        get_data = core_services.CoreServices.get_template_data
        temp['services'] = get_data(template_id, '/services')
        return temp

    @request_statistics.stats_count(API_NAME, 'Update')
    def update(self, request, template_id, body):
        """It updates the description template.
        :param request: the operation request.
        :param template_id: the template ID.
        :param body: the description to be updated
        :return: the updated template description.
        """
        LOG.debug('Environments:Update <Id: {0}, '
                  'Body: {1}>'.format(template_id, body))
        target = {"template_id": template_id}
        policy.check('update_template', request.context, target)

        self._validate_request(request, template_id)
        try:
            LOG.debug('TEMP NAME: {0}>'.format(body['name']))
            if not VALID_NAME_REGEX.match(str(body['name'])):
                msg = _('Template must contain only alphanumeric '
                    'or "_-." characters, must start with alpha')
                LOG.exception(msg)
                raise exc.HTTPClientError(msg)
        except Exception:
                msg = _('Template body is incorrect')
                LOG.exception(msg)
                raise exc.HTTPClientError(msg)

        template = templates.TemplateServices.update(template_id, body)
        return template.to_dict()

    @request_statistics.stats_count(API_NAME, 'Delete')
    def delete(self, request, template_id):
        """It deletes the template.
        :param request: the operation request.
        :param template_id: the template ID.
        """
        LOG.debug('Templates:Delete <Id: {0}>'.format(template_id))
        target = {"template_id": template_id}
        policy.check('delete_template', request.context, target)
        self._validate_request(request, template_id)
        templates.TemplateServices.delete(template_id)
        templates.TemplateServices.remove(template_id)
        return

    @request_statistics.stats_count(API_NAME, 'Createenvironment')
    def createenvironment(self, request, template_id, body):
        LOG.debug('Templates:Create environment <Id: {0}>'.
            format(template_id))
        return

    def _validate_request(self, request, template_id):
        if not templates.TemplateServices.template_exist(template_id):
            LOG.exception(_('Template <TempId {0}> is not found').format(
                template_id))
            raise exc.HTTPNotFound
        template = templates.TemplateServices.get_template(template_id)
        if template.tenant_id != request.context.tenant:
            LOG.exception(_('User is not authorized to access '
                       'this tenant resources.'))
            raise exc.HTTPUnauthorized


def create_resource():
    return wsgi.Resource(Controller())
