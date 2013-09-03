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

from gcecloudstack.models.client import Client
from gcecloudstack.models.accesstoken import AccessToken
from gcecloudstack.models.refreshtoken import RefreshToken
from pyoauth2.provider import AuthorizationProvider
from gcecloudstack import app, db
from flask import session
from . import requester
import json


class CloudstackAuthorizationProvider(AuthorizationProvider):

    def validate_client_id(self, client_id):
        return client_id is not None

    def validate_client_secret(self, client_id, client_secret):
        response = requester.cloud_login(client_id, client_secret)
        if response:
            jsessionid = response.cookies['JSESSIONID']

            data = json.loads(response.text)
            sessionkey = data['loginresponse']['sessionkey']

            existingClient = Client.query.get(client_id);
            client = Client(username=client_id,jsessionid=jsessionid,sessionkey=sessionkey)
            if existingClient is not None:
                existingClient.jsessionid = jsessionid
                existingClient.sessionkey = sessionkey
            else:
                db.session.add(client)

            db.session.commit()

            return True
        else:
            return False

    def validate_redirect_uri(self, client_id, redirect_uri):
        return True

    def validate_access(self):
        return session.user is not None

    def validate_scope(self, client_id, scope):
        return True

    def persist_authorization_code(self, client_id, code, scope):
        return

    def persist_token_information(self, client_id, scope, access_token,
                                  token_type, expires_in,
                                  refresh_token, data):
        client = Client.query.get(client_id)
        if client is not None:
            existingAccessToken = AccessToken.query.filter_by(client_id=client_id).first()
            existingRefreshToken = RefreshToken.query.filter_by(client_id=client_id).first()

            if existingAccessToken is not None:
                existingAccessToken.access_token = access_token
                existingAccessToken.data = json.dumps(data)
                existingAccessToken.expires_in = expires_in
            else:
                db.session.add(AccessToken(access_token=access_token, client_id=client_id, expires_in=expires_in, data=json.dumps(data)))

            if existingRefreshToken is not None:
                existingRefreshToken.refresh_token = refresh_token
                existingAccessToken.data = json.dumps(data)
            else:
                db.session.add(RefreshToken(refresh_token=refresh_token, client_id=client_id, data=json.dumps(data)))

            db.session.commit()
            return True
        else:
            return False

    def from_authorization_code(self, client_id, code, scope):
        return {
            'client_id': client_id,
            'code': code,
            'scope': scope,
        }

    def from_refresh_token(self, client_id, refresh_token, scope):
        refresh_token = RefreshToken.query.get(refresh_token)
        if refresh_token is not None:
            data = json.loads(refresh_token['data'])
            if (scope == '' or scope == data.get('scope')) and client_id == data.get('client_id'):
                return data
        else:
            return False

    def discard_authorization_code(self, client_id, code):
        return None

    def discard_refresh_token(self, client_id, refresh_token):
        refresh_token = RefreshToken.query.get(refresh_token)
        db.session.delete(refresh_token)
        db.session.commit()
