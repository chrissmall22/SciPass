#!/usr/bin/python

# Copyright (C) 2014 Hewlett-Packard Development Company, L.P
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

import HPVAN

def start_scipass_van():

    username = "sdn"
    password = "skyline"
    controller = "15.126.229.78"
    van = HPVAN(username, password, controller)
    van.start_rest("127.0.0.1",8090)


if __name__ == '__main__':
    start_scipass_van()


