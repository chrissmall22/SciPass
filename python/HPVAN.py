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


class SciPassRest():
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

    def run_server(self):
        run('scipass',host='localhost', port=8080)

class HPVAN():
    
    def __init__(self):

        self.datapaths = {}

        # Set Logger
        self.logger = logging.getLogger(__name__)

        #--- register for configuration options
        self.CONF = cfg.CONF
        self.CONF.register_opts([
                cfg.StrOpt('SciPassConfig',default='/etc/SciPass/SciPass.xml',
                           help='where to find the SciPass config file'),
                ])
        
        self.logger.error("Starting SciPass")
        #


        api = SciPass(logger = self.logger,
                      config_file = self.CONF.SciPassConfig )
        
        api.registerForwardingStateChangeHandler(self.changeSwitchForwardingState)

        self.api = api

        # Start REST interface
        SciPassRest(api).run_server()
        
    def connect_controller(self, controller, port, username, password):


        self.logger.debug("Connecting to VAN controller" + controller)

        auth = hp.XAuthToken(user=username, password=password, server=controller)
        api = hp.Api(controller=controller, auth=auth)
        
    def changeSwitchForwardingState(self, dpid=None, header=None, actions=None, command=None, idle_timeout=None, hard_timeout=None, priority=1):
        self.logger.debug("Changing switch forwarding state")
        
        if(not self.datapaths.has_key(dpid)):
            self.logger.error("unable to find switch with dpid " + dpid)
            self.logger.error(self.datapaths)
            return
        
        datapath = self.datapaths[dpid]

        ofp      = datapath.ofproto
        parser   = datapath.ofproto_parser

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

        if(obj['dl_type'] == None):
            match = parser.OFPMatch( in_port     = obj['in_port'],
                                     nw_dst      = obj['nw_dst'],
                                     nw_dst_mask = obj['nw_dst_mask'],
                                     nw_src      = obj['nw_src'],
                                     nw_src_mask = obj['nw_src_mask'],
                                     tp_src      = obj['tp_src'],
                                     tp_dst      = obj['tp_dst'])
        else:
            
            match = parser.OFPMatch( in_port     = obj['in_port'],
                                     nw_dst      = obj['nw_dst'],
                                     nw_dst_mask = obj['nw_dst_mask'],
                                     nw_src      = obj['nw_src'],
                                     nw_src_mask = obj['nw_src_mask'],
                                     dl_type     = obj['dl_type'],
                                     tp_src      = obj['tp_src'],
                                     tp_dst      = obj['tp_dst'])
            
        self.logger.debug("Match: " + str(match))
        
        of_actions = []
        for action in actions:
            if(action['type'] == "output"):
                of_actions.append(parser.OFPActionOutput(int(action['port']),0))
                
        self.logger.debug("Actions: " + str(of_actions))
        if(command == "ADD"):
            command = ofp.OFPFC_ADD
        elif(command == "DELETE_STRICT"):
            command = ofp.OFPFC_DELETE_STRICT
        else:
            command = -1

        self.logger.debug("Sending flow mod with command: " + str(command))
        self.logger.debug("Datpath: " + str(datapath))

        mod = parser.OFPFlowMod( datapath     = datapath,
                                 priority     = int(priority),
                                 match        = match,
                                 cookie       = 0,
                                 command      = command,
                                 idle_timeout = int(idle_timeout),
                                 hard_timeout = int(hard_timeout),
                                 actions      = of_actions)

        if(datapath.is_active == True):
            datapath.send_msg(mod)
            
    def flushRules(self, dpid):
        if(not self.datapaths.has_key(dpid)):
            self.logger.error("unable to find switch with dpid " + dpid)
            return
        
        datapath = self.datapaths[dpid]
        ofp      = datapath.ofproto
        parser   = datapath.ofproto_parser

         # --- create flowmod to control traffic from the prefix to the interwebs
        match = parser.OFPMatch()
        mod = parser.OFPFlowMod(datapath,match,0,ofp.OFPFC_DELETE)
        
         #--- remove mods in the flowmod cache
        self.flowmods[dpid] = []
        
        
         #--- if dp is active then push the rules
        if(datapath.is_active == True):
            datapath.send_msg(mod)
            
    def synchRules(self, dpid):
      #--- routine to syncronize the rules to the DP
      #--- currently just pushes, somday should diff
         
      #--- yep thats a hack, need to think about what multiple switches means for scipass
         if(not self.datapaths.has_key(dpid)):
             self.logger.error("unable to find switch with dpid " + dpid)
             return

         datapath = self.datapaths[dpid]
         if(datapath.is_active == True):
             for mod in self.flowmods:
                 datapath.send_msg(mod)

    def _stats_loop(self):
         while 1:
          #--- send stats request
             for dp in self.datapaths.values():
                 self._request_stats(dp)
                 
             #--- sleep
             hub.sleep(self.statsInterval)

    def _balance_loop(self):
         while 1:
             self.logger.debug("here!!")
             #--- tell the system to rebalance
             self.api.run_balancers()
             #--- sleep
             hub.sleep(self.balanceInterval)

    def _request_stats(self,datapath):
        ofp    = datapath.ofproto
        parser = datapath.ofproto_parser

        cookie = cookie_mask = 0
        match  = parser.OFPMatch()
        req    = parser.OFPFlowStatsRequest(	datapath, 
						0,
						match,
        					#ofp.OFPTT_ALL,
						0xff,
        					ofp.OFPP_NONE)
						#0xffffffff,
        					#cookie, 
						#cookie_mask,
        					#match)
        datapath.send_msg(req)

        req = parser.OFPPortStatsRequest(datapath, 0, ofp.OFPP_NONE)
        datapath.send_msg(req)

  
