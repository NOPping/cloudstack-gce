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
from gcecloudstack.controllers import errors, zones, images, machine_type
from flask import jsonify, request, url_for
import json


def _get_virtualmachine_id(virtualmachine, authorization):
    command = 'listVirtualMachines'
    args = {}
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )
    virtualmachine_id = None
    cloudstack_response = json.loads(cloudstack_response)
    if cloudstack_response['listvirtualmachinesresponse']:
        virtualmachine_id = cloudstack_response[
            'listvirtualmachinesresponse']['virtualmachine'][0]['id']
    return virtualmachine_id


def _cloudstack_virtualmachine_to_gce(response_item):
    return ({
        'kind': 'compute#instance',
        'id': '',
        'creationTimestamp': '',
        'zone': response_item['zonename'],
        'status': response_item['state'],
        'statusMessage': '',
        'name': response_item['name'],
        'description': '',
        'tags': {
            'items': [
                ''
            ],
            'fingerprint': ''
            },
        'machineType': '',
        'image': '',
        'kernel': '',
        'canIpForward': '',
        'networkInterfaces': [
            {
                'network': response_item['nic'][0]['networkname'],
                'networkIP': response_item['nic'][0]['ipaddress'],
                'name': '',
                'accessConfigs': [
                    {
                        'kind': 'compute#accessConfig',
                        'type': '',
                        'name': '',
                        'natIP': ''
                    }
                ]
            }
        ],
        'disks': [
            {
                'kind': 'compute#attachedDisk',
                'index': 0,
                'type': '',
                'mode': '',
                'source': '',
                'deviceName': '',
                'boot': 'true'
            }
        ],
        'metadata': {
            'kind': 'compute#metadata',
            'fingerprint': '',
            'items': [
                {
                    'key': '',
                    'value': ''
                }
            ]
        },
        'serviceAccounts': [
            {
                'email': '',
                'scopes': [
                    ''
                ]
            }
        ],
        'selfLink': ''
    })


def _cloudstack_delete_to_gce(cloudstack_response, instance, instanceid):
    return({
        'kind': 'compute#operation',
        'id': 0,
        'creationTimestamp': '',
        'name': '',
        'zone': '',
        'clientOperationId': '',
        'operationType': '',
        'targetLink': '',
        'targetId': 0,
        'status': '',
        'statusMessage': '',
        'user': '',
        'progress': '',
        'insertTime': '',
        'startTime': '',
        'endTime': '',
        'error': {
            'errors': [
                {
                  'code': '',
                    'location': '',
                    'message': ''
                }
            ]
        },
        'warnings': [
            {
                'code': '',
                'message': '',
                'data': [
                    {
                        'key': '',
                        'value': ''
                    }
                ]
            }
        ],
        'httpErrorStatusCode': 0,
        'httpErrorMessage': '',
        'selfLink': '',
        'region': ''
    })


@app.route('/' + app.config['PATH'] + '<projectid>/aggregated/instances',
           methods=['GET'])
@authentication.required
def aggregatedlistinstances(projectid, authorization):
    command = 'listVirtualMachines'
    args = {}
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

    cloudstack_response = json.loads(cloudstack_response)

    instances = []
    if cloudstack_response['listvirtualmachinesresponse']:
        for response_item in cloudstack_response[
                'listvirtualmachinesresponse']['virtualmachine']:
            instances.append(
                _cloudstack_virtualmachine_to_gce(response_item))

        zonelist = zones.get_zone_names(authorization)

    items = {}
    for zone in zonelist:
        zone_instances = []
        if instances:
            for instance in instances:
                instance['zone'] = zone
                instance['selfLink'] = request.base_url + \
                    '/' + instance['name']
                zone_instances.append(instance)
        else:
            zone_instances.append(errors.no_results_found(zone))

        items['zone/' + zone] = {}
        items['zone/' + zone]['zone'] = zone
        items['zone/' + zone]['instances'] = zone_instances

    populated_response = {
        'kind': 'compute#instanceAggregatedList',
        'id': 'projects/' + projectid + '/instances',
        'selfLink': request.base_url,
        'items': items,
        'nextPageToken': ''
    }

    res = jsonify(populated_response)
    res.status_code = 200
    return res


@app.route('/' + app.config['PATH'] + '<projectid>/zones/<zone>/instances',
           methods=['GET'])
@authentication.required
def listinstances(projectid, authorization, zone):
    command = 'listVirtualMachines'
    args = {}
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

    cloudstack_response = json.loads(cloudstack_response)

    instances = []
    if cloudstack_response['listvirtualmachinesresponse']:
        for response_item in cloudstack_response[
                'listvirtualmachinesresponse']['virtualmachine']:
            instances.append(
                _cloudstack_virtualmachine_to_gce(response_item))

    populated_response = {
        'kind': 'compute#instanceList',
        'id': 'projects/' + projectid + '/instances',
        'selfLink': request.base_url,
        'items': instances,
        'nextPageToken': ''
    }

    res = jsonify(populated_response)
    res.status_code = 200
    return res


@app.route('/' + app.config['PATH'] +
           '<projectid>/zones/<zone>/instances/<instance>', methods=['GET'])
@authentication.required
def getinstance(projectid, authorization, zone, instance):
    command = 'listVirtualMachines'
    args = {
        'keyword': instance
    }
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

    cloudstack_response = json.loads(cloudstack_response)

    if cloudstack_response['listvirtualmachinesresponse']:
        instance = cloudstack_response[
            'listvirtualmachinesresponse']['virtualmachine']
        res = jsonify(instance)
        res.status_code = 200
    else:
        func_route = url_for('getinstance', projectid=projectid,
                             instance=instance, zone=zone)
        res = errors.resource_not_found(func_route)

    return res


@app.route('/' + app.config['PATH'] +
           '<projectid>/zones/<zone>/instances/<instance>', methods=['DELETE'])
@authentication.required
def deleteinstance(projectid, authorization, zone, instance):
    command = 'destroyVirtualMachine'
    instanceid = _get_virtualmachine_id(instance, authorization)
    if instanceid is None:
        func_route = url_for('deleteinstance', projectid=projectid,
                             instance=instance, zone=zone)
        return(errors.resource_not_found(func_route))

    args = {
        'id': instanceid
    }
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

    instance_deleted = _cloudstack_delete_to_gce(
        cloudstack_response,
        instance,
        instanceid
    )

    res = jsonify(instance_deleted)
    res.status_code = 200
    return res


@app.route('/' + app.config['PATH'] +
           '<projectid>/zones/<zone>/instances', methods=['POST'])
@authentication.required
def addinstance(projectid, authorization, zone):

    # TODO: Clean this up
    data = json.loads(request.data)
    service_offering_id = machine_type.get_service_offering_id(
        data['machineType'].rsplit('/', 1)[1],
        authorization
    )
    template_id = images.get_template_id(
        data['image'].rsplit('/', 1)[1],
        authorization
    )
    zone_id = zones.get_zone_id(zone, authorization)
    instance_name = data['name']

    app.logger.debug(
        projectid + '\n' +
        zone + '\n' +
        instance_name + '\n' +
        service_offering_id + '\n' +
        template_id + '\n' +
        zone_id
    )

    command = 'deployVirtualMachine'
    args = {
        'zoneId': zone_id,
        'templateId': template_id,
        'serviceofferingid': service_offering_id,
        'displayname': instance_name,
        'name': instance_name
    }

    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

    cloudstack_response = json.loads(cloudstack_response)

    app.logger.debug(
        json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
    )

    command = 'queryAsyncJobResult'
    args = {
        'jobId': cloudstack_response['deployvirtualmachineresponse']['jobid']
    }

    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

    cloudstack_response = json.loads(cloudstack_response)

    app.logger.debug(
        json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
    )

    return None
