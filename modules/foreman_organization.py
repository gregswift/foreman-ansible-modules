#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2016, Eric D Helms <ericdhelms@gmail.com>
# (c) 2017, Matthias M Dellweg <dellweg@atix.de> (ATIX AG)
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: foreman_organization
short_description: Manage Foreman Organization
description:
    - Manage Foreman Organization
author:
    - "Eric D Helms (@ehelms)"
    - "Matthias M Dellweg (@mdellweg) ATIX AG"
requirements:
    - "nailgun >= 0.28.0"
    - "python >= 2.6"
options:
    server_url:
        description:
            - URL of Foreman server
        required: true
    username:
        description:
            - Username on Foreman server
        required: true
    password:
        description:
            - Password for user accessing Foreman server
        required: true
    verify_ssl:
        description:
            - Verify SSL of the Foreman server
        required: false
        default: true
        type: bool
    name:
        description:
            - Name of the Foreman organization
        required: true
    state:
        description:
            - State of the Organization
        required: true
        choices:
            - present
            - absent
'''

EXAMPLES = '''
- name: "Create CI Organization"
  foreman_organization:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "My Cool New Organization"
    state: present
'''

RETURN = '''# '''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        create_server,
        ping_server,
        find_entities,
        naildown_entity_state,
    )
    from nailgun.entities import Organization

    HAS_NAILGUN_PACKAGE = True
except:
    HAS_NAILGUN_PACKAGE = False


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.foreman_helper import handle_no_nailgun


def sanitize_organization_dict(organization_dict):
    # This is the only true source for names (and conversions thereof)
    name_map = {
        'name': 'name',
    }
    result = {}
    for key, value in name_map.items():
        if key in organization_dict:
            result[value] = organization_dict[key]
    return result


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            username=dict(required=True, no_log=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            name=dict(required=True),
            state=dict(required=True, choices=['present', 'absent']),
        ),
        supports_check_mode=True,
    )

    handle_no_nailgun(module, HAS_NAILGUN_PACKAGE)

    organization_dict = dict(
        [(k, v) for (k, v) in module.params.items() if v is not None])

    server_url = organization_dict.pop('server_url')
    username = organization_dict.pop('username')
    password = organization_dict.pop('password')
    verify_ssl = organization_dict.pop('verify_ssl')
    state = organization_dict.pop('state')

    try:
        create_server(server_url, (username, password), verify_ssl)
    except Exception as e:
        module.fail_json(msg="Failed to connect to Foreman server: %s " % e)

    ping_server(module)
    try:
        entities = find_entities(Organization, name=organization_dict['name'])
        if len(entities) > 0:
            entity = entities[0]
        else:
            entity = None
    except Exception as e:
        module.fail_json(msg='Failed to find entity: %s ' % e)

    organization_dict = sanitize_organization_dict(organization_dict)

    changed = naildown_entity_state(Organization, organization_dict, entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
