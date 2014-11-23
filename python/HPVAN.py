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
from bottle import run as bottle_run
from bottle import route
from webob import Response

import oslo.config.cfg as cfg
import hpsdnclient as hp
import json

from SciPass import SciPass

ETH_TYPE_IP = 0x0800
_DPID_LEN = 16
_DPID_LEN_STR = str(_DPID_LEN)
_DPID_FMT = '%0' + _DPID_LEN_STR + 'x'
DPID_PATTERN = r'[0-9a-f]{%d}' % _DPID_LEN


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
        self.logger = api.logger

    #POST /scipass/flows/good_flow
    @route('/scipass/flows/good_flow')
    def good_flow(self, req):
        try:
            obj = eval(req.body)
        except SyntaxError:
            self.logger.error("Syntax Error processing good_flow signal %s", req.body)
            return Response(status=400)

        result = self.api.good_flow(obj)
        return Response(content_type='application/json',body=json.dumps(result))

    #POST /scipass/flows/bad_flow
    @route('scipass', '/scipass/flows/bad_flow', methods=['PUT'])
    def bad_flow(self, req):
        try:
            obj = eval(req.body)
        except SyntaxError:
            self.logger.error("Syntax Error processing bad_flow signal %s", req.body)
            return Response(status=400)
        result = self.api.bad_flow(obj)
        return Response(content_type='application/json',body=json.dumps(result))

    #GET /scipass/flows/get_good_flows
    @route('scipass', '/scipass/flows/get_good_flows', methods=['GET'])
    def get_good_flows(self, req):
        result = self.api.get_good_flows()
        return Response(content_type='application/json',body=json.dumps(result))

    #GET /scipass/flows/get_bad_flows
    @route('scipass', '/scipass/flows/get_bad_flows', methods=['GET'])
    def get_bad_flows(self, req):
        result = self.api.get_bad_flows()
        return Response(content_type='application/json',body=json.dumps(result))

    @route('scipass', '/scipass/switch/{dpid}/flows', methods=['GET'], requirements= {'dpid': DPID_PATTERN})
    def get_switch_flows(self, req, **kwargs):
        result = self.api.getSwitchFlows(dpid=kwargs['dpid'])
        return Response(content_type='application/json', body=json.dumps(result))

    @route('scipass', '/scipass/sensor/load', methods=['PUT'])
    def update_sensor_load(self, req):
        try:
            obj = eval(req.body)
        except SyntaxError:
            self.logger.error("Syntax Error processing update_sensor_status signal %s", req.body)
            return Response(status=400)
        result = self.api.setSensorStatus(obj['sensor_id'],obj['load'])
        return Response(content_type='application/json',body=json.dumps(result))

    @route('scipass', '/scipass/switch/{dpid}/domain/{domain}/sensor/{sensor_id}', methods=['GET'], requirements= {'dpid': DPID_PATTERN})
    def get_sensor_load(self, req, **kwargs):
        result = self.api.getSensorStatus(dpid=kwargs['dpid'], domain=kwargs['domain'], sensor_id=kwargs['sensor_id'])
        return Response(content_type='application/json',body=json.dumps(result))

    @route('scipass', '/scipass/switches', methods=['GET'])
    def get_switches(self, req):
        result = self.api.getSwitches()
        return Response(content_type='application/json', body=json.dumps(result))

    @route('scipass', '/scipass/switch/{dpid}/domain/{domain}/sensors', methods=['GET'], requirements = {'dpid': DPID_PATTERN})
    def get_domain_sensors(self, req, **kwargs):
        result = self.api.getDomainSensors(dpid = kwargs['dpid'], domain = kwargs['domain'] )
        return Response(content_type='application/json', body=json.dumps(result))

    @route('scipass', '/scipass/switch/{dpid}/domains', methods=['GET'], requirements = {'dpid': DPID_PATTERN})
    def get_switch_domains(self, req, **kwargs):
        result = self.api.getSwitchDomains(dpid=kwargs['dpid'])
        return Response(content_type='application/json', body=json.dumps(result))

    @route('scipass', '/scipass/switch/{dpid}/domain/{domain}', methods=['GET'], requirements = {'dpid': DPID_PATTERN})
    def get_domain_status(self, req, **kwargs):
        result = self.api.getDomainStatus(dpid = kwargs['dpid'], domain = kwargs['domain'])
        return Response(content_type='application/json', body=json.dumps(result))

    @route('scipass', '/scipass/switch/{dpid}/domain/{domain}/flows',methods=['GET'],requirements = {'dpid': DPID_PATTERN})
    def get_domain_flows(self,req, **kwargs):
        result = self.api.getDomainFlows(dpid = kwargs['dpid'], domain = kwargs['domain'])
        return Response(content_type='application/json', body=json.dumps(result))


class HPVAN():

    def __init__(self, user, pw, controller):

        self.datapaths = {}
        self.username = "sdn"
        self.password = "skyline"
        self.controller = "15.126.229.78"

        logging.basicConfig()
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

        self.logger.debug("Connecting to VAN controller" + self.controller)
        auth = hp.XAuthToken(user=self.username, password=self.password, server=self.controller)
        api = hp.Api(controller=self.controller, auth=auth)


    def start_rest(self, host, port):
        module = "SciPass"
        bottle_run(module,host=host,port=port)


        
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
        #self.flowmods[dpid] = []
        
        
         #--- if dp is active then push the rules
        if(datapath.is_active == True):
            datapath.send_msg(mod)


def start_scipass_van():

    username = "sdn"
    password = "skyline"    
    controller = "15.126.229.78"
    scipass = HPVAN(username, password, controller)
    scipass.start_rest('localhost',8090)


if __name__ == '__main__':
    start_scipass_van()

