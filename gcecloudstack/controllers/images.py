#!/usr/bin/env python
# encoding: utf-8
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from gcecloudstack import app
from gcecloudstack import authentication
from gcecloudstack.services import requester
from gcecloudstack.controllers import helper, errors
from flask import request, url_for

def _get_templates(authorization, args=None):
    command = 'listTemplates'
    if not args:
        args = {}

    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )
    return cloudstack_response


def get_template_id(image, authorization):
    template_id = None
    cloudstack_response = _get_templates(
        authorization,
        args={'keyword': image}
    )
    if cloudstack_response['listtemplatesresponse']:
        template_id = cloudstack_response['listtemplatesresponse']['template'][0]['id']
    return template_id


def _cloudstack_template_to_gce(cloudstack_response, selfLink=None):
    translate_image_status = {
        'True': 'Ready',
        'False': 'Failed'
    }

    response = {}
    response['kind'] = 'compute#image'
    response['id'] = cloudstack_response['id']
    response['creationTimestamp'] = cloudstack_response['created']
    response['name'] = cloudstack_response['name']
    response['description'] = cloudstack_response['displaytext']
    response['status'] = translate_image_status[str(cloudstack_response['isready'])]

    if not selfLink:
        response['selfLink'] = request.base_url
    else:
        response['selfLink'] = selfLink

    return response


@app.route('/' + app.config['PATH'] + 'centos-cloud/global/images', methods=['GET'])
@authentication.required
def listnocentoscloudimages(authorization):
    images = []
    populated_response = _create_populated_image_response('centos-cloud', images)
    return helper.createsuccessfulresponse(data=populated_response)


@app.route('/' + app.config['PATH'] + 'debian-cloud/global/images', methods=['GET'])
@authentication.required
def listnodebiancloudimages(authorization):
    images = []
    populated_response = _create_populated_image_response('debian-cloud', images)
    return helper.createsuccessfulresponse(data=populated_response)


@app.route('/' + app.config['PATH'] + '<projectid>/global/images', methods=['GET'])
@authentication.required
def listimages(projectid, authorization):
    cloudstack_response = _get_templates(
        authorization,
        args = {
            'templatefilter': 'executable'
        }
    )

    images = []
    if cloudstack_response['listtemplatesresponse']:
        for template in cloudstack_response['listtemplatesresponse']['template']:
            images.append(_cloudstack_template_to_gce(template))

    populated_response = _create_populated_image_response(projectid, images)
    return helper.createsuccessfulresponse(data=populated_response)


def _create_populated_image_response(projectid, images):
    populated_response = {
        'kind': 'compute#imageList',
        'selfLink': request.base_url,
        'id': 'projects/' + projectid + '/global/images',
        'items': images
    }
    return populated_response


@app.route('/' + app.config['PATH'] + '<projectid>/global/images/<image>', methods=['GET'])
@authentication.required
def getimage(projectid, authorization, image):
    cloudstack_response = _get_templates(
        authorization,
        args = {
            'templatefilter': 'executable',
            'keyword': image
        }
    )
    if cloudstack_response['listtemplatesresponse']:
        cloudstack_response = _cloudstack_template_to_gce(cloudstack_response['listtemplatesresponse']['template'][0])
        return helper.createsuccessfulresponse(data=cloudstack_response)

    function_route = url_for('getimage', projectid=projectid, image=image)
    return(errors.resource_not_found(function_route))

