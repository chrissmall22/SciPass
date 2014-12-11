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
from SciPass.ofproto import ether

ETH_TYPE_IP = 0x0800
ETH_TYPE_ARP = 0x0806
ETH_TYPE_8021Q = 0x8100
ETH_TYPE_IPV6 = 0x86dd
ETH_TYPE_SLOW = 0x8809
ETH_TYPE_MPLS = 0x8847
ETH_TYPE_8021AD = 0x88a8
ETH_TYPE_LLDP = 0x88cc
ETH_TYPE_8021AH = 0x88e7
ETH_TYPE_IEEE802_3 = 0x05dc
ETH_TYPE_CFM = 0x8902

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
                cfg.StrOpt('SciPassConfig',default='t/etc/SciPass.xml',
                           help='where to find the SciPass config file'),
                ])
        
        self.logger.error("Starting SciPass")
        #
        api = SciPass(logger = self.logger,
                      config_file = self.CONF.SciPassConfig )
        api.registerForwardingStateChangeHandler(self.changeSwitchForwardingState)


        self.logger.debug("Connecting to VAN controller" + self.controller)
        auth = hp.XAuthToken(user=self.username, password=self.password, server=self.controller)
        api = hp.Api(controller=self.controller, auth=auth)
        self.api = api



    def start_rest(self, host, port):
        module = "SciPass"
        bottle_run(module,host=host,port=port)


        
    def changeSwitchForwardingState(self, dpid=None, header=None, actions=None, command=None, idle_timeout=None, hard_timeout=None, priority=1):
        self.logger.debug("Changing switch forwarding state")
        
        if(not self.datapaths.has_key(dpid)):
            self.logger.error("unable to find switch with dpid " + dpid)
            self.logger.error(self.datapaths)
            return
        
        api = self.api
        #ofp      = datapath.ofprotok
        #parser   = datapath.ofproto_parser

        # This assumes IPv4 since SciPass doesn't support IPv6 prefix splitting

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

        # Recreate network with mask
        if obj['nw_dst'] is not None and obj['nw_dst_mask'] is not None:
            new_dst =  obj['nw_dst'] + "/" +  obj['nw_dst']
        else:
            new_dst = None

        if obj['nw_src'] is not None and obj['nw_src_mask'] is not None:
            new_src =  obj['nw_src'] + "/" +  obj['nw_src']
        else:
            new_src = None

        if  obj['dl_type'] is None:
            match = hp.datatypes.Match( in_port     = obj['in_port'],
                                     ipv4_dst      = new_dst,
                                     nw_dst_mask = obj['nw_dst_mask'],
                                     ipv4_src      = new_src,
                                     tcp_src      = obj['tp_src'],
                                     tcp_dst      = obj['tp_dst'])

        else:
            match = hp.datatypes.Match( in_port    = obj['in_port'],
                                     ipv4_dst      = new_dst,
                                     nw_dst_mask   = obj['nw_dst_mask'],
                                     ipv4_src      = new_src,
                                     dl_type       = obj['dl_type'],
                                     tcp_src      = obj['tp_src'],
                                     tcp_dst      = obj['tp_dst'])
            
        self.logger.debug("Match: " + str(match))
        
        of_actions = []

        # Get OF version of Datapath
        of_version = self._get_datapath_version(dpid)

        for action in actions:
            if(action['type'] == "output"):
                 if of_version == "1.0.0":
                     of_actions = hp.datatypes.Action(output=int(action['port'])).append

        # Todo: Handle Instructions for OF 1.1x switches
        #if of_version != "1.0.0":
        #    of_instructions = hp.datatypes.Instruction(output=)
        self.logger.debug("Actions: " + str(of_actions))

        flow = hp.datatypes.Flow(priority=30000, idle_timeout=30,
                                 match=match, actions=of_actions)
        if(command == "ADD"):
            api.add_flows(dpid,flow)
        elif(command == "DELETE_STRICT"):
            api.delete_flows(dpid,flow)
        else:
            command = -1

        self.logger.debug("Sending flow mod with command: " + str(command))
        self.logger.debug("DPID: " + str(dpid))

            
    def flushRules(self, dpid):
        if(not self.datapaths.has_key(dpid)):
            self.logger.error("unable to find switch with dpid " + dpid)
            return

        api = self.api

        # Match all Flows
        match = hp.datatypes.Match()
        flows = hp.datatypes.Flow(match=match)
        api.delete_flows(dpid,flows)


    def _get_datapath_version(self,dpid):
        default_version = "1.0.0"
        self.logger.debug("Getting DPID Version from controller for DPID %s" + str(dpid))
        api = self.api
        try:
            datapath = api.get_datapath_detail(dpid)
        except:
            self.logger.debug("Can't get DPID Version, Setting version 1.0.0 for DPID" + str(dpid))
            return default_version
        return datapath.negotiated_version


def start_scipass_van():

    username = "sdn"
    password = "skyline"    
    controller = "15.126.229.78"
    scipass = HPVAN(username, password, controller)
    scipass.start_rest('localhost',8090)


if __name__ == '__main__':
    start_scipass_van()

