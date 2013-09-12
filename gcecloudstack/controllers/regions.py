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
from gcecloudstack.services import requester
from flask import jsonify
import json

@app.route('/' + app.config['PATH'] + '<projectid>/regions')
@authentication.required
def listregion(projectid, authorization):

    command = 'listRegions'
    args = {}
    logger = None
    cloudstack_response = requester.make_request(
        command,
        args,
        logger,
        authorization.jsessionid,
        authorization.sessionkey
    )

    cloudstack_response = json.loads(cloudstack_response)
    cloudstack_response = cloudstack_response['listregionsresponse']

    regions = []

    # test for empty response, i.e no zones available
    if cloudstack_response:
        for region in cloudstack_response['region']:
            regions.append({
                'kind': "compute#region",
                'name': region['name'],
                'description': region['name'],
                'id': region['id'],
                'status': region['allocationstate']
            })

    populated_response = {
        'kind': "compute#regionList",
        'id': '',
        'selfLink': '',
        'items': regions
    }

    res = jsonify(populated_response)
    res.status_code = 200
    return res


@app.route('/' + app.config['PATH'] + '<projectid>/regions/<region>')
@authentication.required
def listregion(projectid, authorization, region):

    command = 'listRegions'
    args = { 'name' : region}
    logger = None
    cloudstack_response = requester.make_request(
        command,
        args,
        logger,
        authorization.jsessionid,
        authorization.sessionkey
    )

    cloudstack_response = json.loads(cloudstack_response)
    cloudstack_response = cloudstack_response['listregionsresponse']['region'][0]

    # test for empty response, i.e no region available
    if cloudstack_response:
        region = {'kind': "compute#region",
                  'name': cloudstack_response['name'],
                  'id': cloudstack_response['id'],
                  'selfLink': cloudstack_response['endpoint']
                 }

    res = jsonify(region)
    res.status_code = 200
    return res