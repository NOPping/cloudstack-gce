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


from gstack import app
from gstack import helpers
from gstack import controllers
from gstack import authentication
from gstack.controllers import errors
from flask import request, url_for


def _cloudstack_account_to_gce(cloudstack_response):
    response = {}
    response['kind'] = 'compute#region'
    response['description'] = cloudstack_response['name']
    response['name'] = cloudstack_response['name']
    response['id'] = cloudstack_response['id']
    response['status'] = 'UP'
    return response


@app.route('/compute/v1/projects/<projectid>/regions', methods=['GET'])
@authentication.required
def listregions(projectid, authorization):
    args = {'command':'listAccounts'}
    kwargs = {}
    items = controllers.describe_items(
        authorization, args, 'account',
        _cloudstack_account_to_gce, **kwargs)

    populated_response = {
        'kind': 'compute#regionList',
        'id': 'projects/' + projectid + '/regions',
        'selfLink': request.base_url,
        'items': items
    }
    return helpers.create_response(data=populated_response)


@app.route('/compute/v1/projects/<projectid>/regions/<region>', methods=['GET'])
@authentication.required
def getregion(projectid, authorization, region):
    cloudstack_response = _get_regions(
        authorization=authorization,
        args={'name': region}
    )

    if region == cloudstack_response['listregionsresponse']['region'][0]['name']:
        return helpers.create_response(
            data=_cloudstack_account_to_gce(
                cloudstack_response['listregionsresponse']['region'][0]
            )
        )
    else:
        function_route = url_for('getregion', projectid=projectid, region=region)
        return errors.resource_not_found(function_route)
