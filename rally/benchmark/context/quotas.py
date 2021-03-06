# Copyright 2014: Dassault Systemes
# All Rights Reserved.
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

from rally.benchmark.context import base
from rally import osclients


class NovaQuotas(object):
    """Management of Nova quotas."""

    QUOTAS_SCHEMA = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "instances": {
                "type": "integer",
                "minimum": -1
            },
            "cores": {
                "type": "integer",
                "minimum": -1
            },
            "ram": {
                "type": "integer",
                "minimum": -1
            },
            "floating-ips": {
                "type": "integer",
                "minimum": -1
            },
            "fixed-ips": {
                "type": "integer",
                "minimum": -1
            },
            "metadata-items": {
                "type": "integer",
                "minimum": -1
            },
            "injected-files": {
                "type": "integer",
                "minimum": -1
            },
            "injected-file-content-bytes": {
                "type": "integer",
                "minimum": -1
            },
            "injected-file-path-bytes": {
                "type": "integer",
                "minimum": -1
            },
            "key-pairs": {
                "type": "integer",
                "minimum": -1
            },
            "security-groups": {
                "type": "integer",
                "minimum": -1
            },
            "security-group-rules": {
                "type": "integer",
                "minimum": -1
            }
        }
    }

    def __init__(self, client):
        self.client = client

    def update(self, endpoint, **kwargs):
        self.client.quotas.update(endpoint, **kwargs)

    def delete(self, endpoint):
        # Reset quotas to defaults and tag database objects as deleted
        self.client.quotas.delete(endpoint)


class CinderQuotas(object):
    """Management of Cinder quotas."""

    QUOTAS_SCHEMA = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "gigabytes": {
                "type": "integer",
                "minimum": -1
            },
            "snapshots": {
                "type": "integer",
                "minimum": -1
            },
            "volumes": {
                "type": "integer",
                "minimum": -1
            }
        }
    }

    def __init__(self, client):
        self.client = client

    def update(self, endpoint, **kwargs):
        self.client.quotas.update(endpoint, **kwargs)

    def delete(self, endpoint):
        # Currently, no method to delete quotas available in cinder client:
        # Will be added with https://review.openstack.org/#/c/74841/
        pass


class Quotas(base.Context):
    """Context class for updating benchmarks' tenants quotas."""

    __ctx_name__ = "quotas"

    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": "http://json-schema.org/draft-03/schema",
        "additionalProperties": False,
        "properties": {
            "nova": NovaQuotas.QUOTAS_SCHEMA,
            "cinder": CinderQuotas.QUOTAS_SCHEMA,
        }
    }

    def __init__(self, context):
        super(Quotas, self).__init__(context)
        self.clients = osclients.Clients(context["admin"]["endpoint"])
        self.nova_quotas = NovaQuotas(self.clients.nova())
        self.cinder_quotas = CinderQuotas(self.clients.cinder())

    def setup(self):
        for tenant in self.context["tenants"]:
            if "nova" in self.config and len(self.config["nova"]) > 0:
                self.nova_quotas.update(tenant["id"],
                                        **self.config["nova"])

            if "cinder" in self.config and len(self.config["cinder"]) > 0:
                self.cinder_quotas.update(tenant["id"],
                                          **self.config["cinder"])

    def cleanup(self):
        for tenant in self.context["tenants"]:
            # Always cleanup quotas before deleting a tenant
            self.nova_quotas.delete(tenant["id"])
            self.cinder_quotas.delete(tenant["id"])
