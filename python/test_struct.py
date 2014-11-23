# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
# Copyright (C) 2014 The Trustees of Indiana University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from bottle import run, route

import oslo.config.cfg as cfg
import hpsdnclient as hp

from SciPass import SciPass

ETH_TYPE_IP = 0x0800


"""
 Forwarding rule Priorities
   BlackList  
   WhiteList
   Balancer 
   Default
"""


class TestRest():
    def __init__(self, api):
        self.api = api

    #GET /scipass/test
    @route('/scipass/test')
    def test(self):
        return "test"

    @route('/scipass/flows')
    def test(self):
        flows = self.api.get_food_flows
        return flows


class TestVAN():

    def __init__(self, user, pw, controller):

        logging.basicConfig()
        self.logger = logging.getLogger(__name__)

        #--- register for configuration options
        self.CONF = cfg.CONF
        self.CONF.register_opts([
                cfg.StrOpt('SciPassConfig',default='../etc/SciPass/SciPass.xml',
                           help='where to find the SciPass config file'),
                ])
        
        self.logger.error("Starting SciPass")
        #
        api = SciPass(logger = self.logger,
                      config_file = self.CONF.SciPassConfig )
        api.registerForwardingStateChangeHandler(self.changeSwitchForwardingState)

        self.api = api

        self.logger.debug("Connecting to VAN controller" + controller)
        auth = hp.XAuthToken(user=user, password=pw, server=controller)
        api = hp.Api(controller=controller, auth=auth)

        run("scipass", host="127.0.0.1", port=8080)


        
    def changeSwitchForwardingState(self, dpid=None, header=None, actions=None, command=None, idle_timeout=None, hard_timeout=None, priority=1):
        self.logger.debug("Changing switch forwarding state")


        obj = {} 
        
        if(header.has_key('dl_type')):
            if(header['dl_type'] == None):
                obj['dl_type'] = None
            else:
                obj['dl_type'] = int(header['dl_type'])
        else:
            obj['dl_type'] = ETH_TYPE_IP
            
        if(header.has_key('phys_port')):
            obj['in_port'] = int(header['phys_port'])
        else:
            obj['in_port'] = None
            
        if(header.has_key('nw_src')):
            obj['nw_src'] = int(header['nw_src'])
        else:
            obj['nw_src'] = None
             
        if(header.has_key('nw_src_mask')):
            obj['nw_src_mask'] = int(header['nw_src_mask'])
        else:
            obj['nw_src_mask'] = None
         
        if(header.has_key('nw_dst')):
            obj['nw_dst'] = int(header['nw_dst'])
        else:
            obj['nw_dst'] = None

        if(header.has_key('nw_dst_mask')):
            obj['nw_dst_mask'] = int(header['nw_dst_mask'])
        else:
            obj['nw_dst_mask'] = None

        if(header.has_key('tp_src')):
            obj['tp_src'] = int(header['tp_src'])
        else:
            obj['tp_src'] = None

        if(header.has_key('tp_dst')):
            obj['tp_dst'] = int(header['tp_dst'])
        else:
            obj['tp_dst'] = None

            
    def flushRules(self, dpid):
       print dpid



def start_scipass_van():

    username = "sdn"
    password = "skyline"
    controller = "15.126.229.78"
    scipass = TestVAN(username, password, controller)



if __name__ == '__main__':
    start_scipass_van()

