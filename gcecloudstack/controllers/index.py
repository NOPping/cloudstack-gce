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
from flask import jsonify
import json
import os

@app.route('/example')
@authentication.required
def example(authorization):
    resp = jsonify({
            "jsessionid": authorization.jsessionid,
            "sessionkey": authorization.sessionkey,
        })
    resp.status_code = 200
    return resp

@app.route('/compute/v1beta15/projects/<projectid>/zones')
@authentication.required
def listzones(projectid,authorization):
    command = 'listZones'
    args = None
    logger = None
    response = requester.make_request(command, args, logger, authorization.jsessionid, authorization.sessionkey)
    print response
    response = json.loads(response)
    response = response['listzonesresponse']['zone']
    basepath = os.path.dirname(__file__)
    listzones_template = open(os.path.join(basepath,"..", "templates/listzones.json"), "r").read()
    listzones_template = json.loads(listzones_template)
    
    resp = jsonify(listzones_template)
    resp.status_code = 200
    return resp

@app.route('/compute/v1beta15/projects/<projectid>')
@authentication.required
def getProject(projectid,authorization):

    basepath = os.path.dirname(__file__)
    getproject_template = open(os.path.join(basepath,"..", "templates/getproject.json"), "r")
    getproject_template = json.loads(getproject_template.read())
    resp = jsonify(getproject_template)

    resp = jsonify(getproject_template)
    resp.status_code = 200

    return resp

@app.route('/discovery/v1/apis/compute/v1beta15/rest')
def discovery():

    basepath = os.path.dirname(__file__)
    discovery_template = open(os.path.join(basepath,"..", "templates/discovery.json"), "r")
    discovery_template = json.loads(discovery_template.read())
    resp = jsonify(discovery_template)

    resp.status_code = 200
    return resp
