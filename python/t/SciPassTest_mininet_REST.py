# Version of the SciPass tests that intergrates a mininet instance 
# Provides an easy way to test without a physical switch and/or with more complex topologies 
import os.path
import unittest
from urlparse import urlparse

import sys
sys.path.append(".")
from HPVAN import SciPassRest
from mock import patch


def fake_urlopen(url):
    """
    A stub urlopen() implementation that load json responses from
    the filesystem.
    """
    # Map path from url to a file
    parsed_url = urlparse(url)
    resource_file = os.path.normpath('t/resources%s' % parsed_url.path)
    # Must return a file-like object
    return open(resource_file, mode='rb')


class SciPassRestTestCase(unittest.TestCase):
    """Test case for the SCI Pass REST interface methods."""

    def setUp(self):
        #self.patcher = patch('client.urlopen', fake_urlopen)
        #self.patcher.start()
        self.scipassrest = SciPassRest()

    #def tearDown(self):
    #    self.patcher.stop()

    def test_good_flows(self):
        """Push a sample good flow into rest interface then get the same result back"""

        id = 1
        req = '{"nw_src": "10.0.20.2/32", "nw_dst":"156.56.6.1/32", "tp_src":1, "tp_dst":2}'
        flows = self.scipassrest.good_flow(req)
        print "Flows %s" % flows
        self.assertEquals(len(flows),2)
        flow = flows[0]
        self.assertEqual(int(flow['hard_timeout']),0)
        self.assertEqual(int(flow['idle_timeout']),90)
        self.assertEqual(flow['actions'],[{'type': 'output', 'port': '3'}])
        self.assertEqual(flow['header'],{'phys_port': 2, 'nw_src_mask': 32, 'nw_dst_mask': 32, 'nw_src': 167777282, 'tp_dst': 2, 'tp_src': 1, 'nw_dst': 2620917249})
        self.assertEqual(int(flow['priority']),900)
        self.assertEqual(flow['command'],"ADD")
        self.assertEqual(flow['dpid'],"%016x" % id)
        flow = flows[1]
        self.assertEqual(int(flow['hard_timeout']),0)
        self.assertEqual(int(flow['idle_timeout']),90)
        self.assertEqual(flow['actions'],[{'type': 'output', 'port': '2'}])
        self.assertEqual(flow['header'],{'phys_port': 3, 'nw_src_mask': 32, 'nw_dst_mask': 32, 'nw_dst': 167777282, 'tp_dst': 1, 'tp_src': 2, 'nw_src': 2620917249})
        self.assertEqual(int(flow['priority']),900)
        self.assertEqual(flow['command'],"ADD")
        self.assertEqual(flow['dpid'],"%016x" % id)





