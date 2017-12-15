"""
    This program is launched in 5 minutes intervals and checks
    if it should turn on ports on switch located in dormitory
    This program has to be launched from local SPSE network
    because it uses local IP to connect to the switch, but
    you can control it from anywhere thanks to checking
    public url http://dev.jozefcipa.com/spse-switch

    WARNING !!!
    This program is NOT INTENDED to be used to damage or harm
    network devices and cannot be used in production network.
    It was made only for educational purposes and as demonstration.
    (c) 2017 Jozef Cipa
"""

import requests
import json
import sys
import os
from random import randint
import logging
import credentials

# Port numbers
from room_groups import room_groups

# Logger setup
logger = logging.getLogger('myapp')
handler = logging.FileHandler('1nternat.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Returns JSON {turnOnPorts: bool}
CONFIRM_URL = 'http://dev.jozefcipa.com/spse-switch'

# URLs to switch
SWITCH_LOGIN_URL = 'http://192.168.30.253/logon/LogonRpm.htm'
SWITCH_TURN_PORT_ON_URL = 'http://192.168.30.253/userRpm/PortStatusSetRpm.htm?\
                            txt_ipaddr=&t_port_name=&state=2&spd=6&flowctrl=1\
                            &chk_{0}=1&submit=Apply'
SWITCH_TURN_PORT_OFF_URL = 'http://192.168.30.253/userRpm/PortStatusSetRpm.htm?\
                            txt_ipaddr=&t_port_name=&state=1&spd=6&flowctrl=1\
                            &chk_{0}=1&submit=Apply'

ROOM_GROUPS_COUNT = 3  # Plus group 1 and 2, A-5 and A-6

# Check if it should turn ports on or off
should_turn_on = False  # Don't turn on by default
should_turn_off = len(sys.argv) == 2 and sys.argv[1] == '--turn-ports-off'
request = None

try:
    request = requests.Session()
    response = request.get(CONFIRM_URL)

    should_turn_on = bool(json.loads(response.text)['turnOnPorts'])
except Exception as e:
    logger.error(e)
    exit(-1)

if should_turn_on:

    status_msg = ''
    try:

        # Login to switch
        request.post(SWITCH_LOGIN_URL, data={
            'username': credentials.SWITCH_USERNAME,
            'password': credentials.SWITCH_PASSWORD,
            'logon': 'Login'
        })

        logger.info('Logged in to switch')

        turned_room_groups = ''
        turned_ports = []

        # Turn on room groups that have `alwaysTurnOn` flag
        for room_group in room_groups:
            if 'alwaysTurnOn' in room_group.keys() and \
            room_group['alwaysTurnOn']:

                for port_number in room_group['ports']:
                    request.get(SWITCH_TURN_PORT_ON_URL.format(port_number))

                    # Append port number to list
                    turned_ports.append(port_number)
                    logger.info('Turning on port ' + str(port_number))

                turned_room_groups += room_group['name'] + ', '

        # Turn on another `ROOM_GROUPS_COUNT` room groups
        i = 0
        while i != ROOM_GROUPS_COUNT:

            random_room_group = room_groups[randint(0, len(room_groups) - 1)]

            # Skip room groups that already have been turned on
            if 'alwaysTurnOn' in random_room_group.keys() and \
            random_room_group['alwaysTurnOn']:
                continue

            for port_number in random_room_group['ports']:
                request.get(SWITCH_TURN_PORT_ON_URL.format(port_number))
                turned_ports.append(port_number)  # Append port number to list
                logger.info('Turning on port ' + str(port_number))

            turned_room_groups += random_room_group['name'] + ', '
            i += 1

        # Save room groups that have been changed
        tmp = open('turned_ports', 'w')
        tmp.write(','.join(str(x) for x in turned_ports))

        logger.info('Switch ports have been turned ON, ' +
        'enabled room groups are ' + turned_room_groups.strip(', '))
    except Exception as e:
        logger.error(str(e))
elif should_turn_off:

    try:
        turned_ports = open('turned_ports', 'r').read().split(',')
    except Exception as e:

        logger.error(str(e))

        # If file not exists, just exit
        exit()

    try:
        # Login to switch
        res = request.post(SWITCH_LOGIN_URL, data={
            'username': credentials.SWITCH_USERNAME,
            'password': credentials.SWITCH_PASSWORD,
            'logon': 'Login'
        }, headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        })

        logger.info('Logged in to switch')

        # Turn off ports in all room groups
        # that have been turned on by this program earlier
        for port_number in turned_ports:
            request.get(SWITCH_TURN_PORT_OFF_URL.format(port_number))
            logger.info('Turning off port ' + port_number)
    except Exception as e:
        logger.error(str(e))

    # Delete temp file
    os.remove('turned_ports')
    logger.info('Switch ports have been turned OFF')
