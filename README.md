[![Build Status](https://travis-ci.org/NOPping/gCloud.png?branch=master)](https://travis-ci.org/NOPping/gCloud)

# Google Compute Engine Interface For Cloudstack

## Proposal

This project aims to provide a new compute API interface for Apache Cloudstack that is compatible with Google Compute Engine [GCE](https://cloud.google.com/products/compute-engine). GCE is Google's Infrastructure-as-a-Service (IaaS) compute service that competes with Amazon Web Services EC2. In short, this is a mapping of the GCE API [reference](https://developers.google.com/compute/docs/reference/latest/) and the CloudStack [API](http://cloudstack.apache.org/docs/api/index.html)

## Implementation

The GCE APIs for Cloudstack is supplied as a layer over the current Cloudstack API. The given application will take in a GCE based API request, pass it over to the Cloudstack API, get the required data and return it in a suitable format.

It is written in Python, using [Flask](http://flask.pocoo.org/) to expose a GCE compliant REST API. Requests, Pycrypto, Pyopenssl and Flask-sqlachemy are dependencies. A custom version of pyoauth2 is included in the source.

In this first early release, the following GCE categories are implemented:
- disks
- firewalls
- images
- instances
- machine type
- global operations
- project
- zones

Caveat: There exists some semantic differences between the two APIs, for example between the concept of zones and regions, projects and domains. This project does a best effort attempt at creating a usable GCE interface to a CloudStack cloud but it may not fit every CloudStack deployment.

##Installation

#Developers

Clone the repository

    git clone https://github.com/NOPping/gCloud.git

Install the package

    python ./setup.py install

This will install a `gcloud` binary in your path. Check the `gcloud/data/config.cfg` and enter the endpoint of your cloud.

Install [gcutil](https://developers.google.com/compute/docs/gcutil/) 

gcloud comes with a self-signed certificate for the local endpoint `gcloud/data/server.crt`, copy the certificate to the gcutil certificates file `gcutil/lib/httplib2/httplib2/cacerts.txt`

At this stage your CloudStack apikey and secretkey need to be entered in the gcutil auth_helper.py file at `gcutil/lib/google_compute_engine/gcutil/auth_helper.py`
This is far from ideal and we opened a featur request with google to pass the `client_id` and `client_secret` as options to gcutil, hopefully future release of gcutil will allow us to do so.

Start gcloud:

    gcloud

Use gcutil with the following parameters (an alias can be useful):

    gcutil --authorization_uri_base=https://localhost:5000/oauth2 --auth_host_name=127.0.0.1 --auth_host_port=9999 --auth_local_webserver=true --api_host="https://localhost:5000/" --fetch_discovery=true

gcutil will issues requests to the local Flask application, get an OAuth token and then issue requests to your CloudStack endpoint

#Users

You can grab the package from Pypi

    pip install gcloud

Then follow the same instructions as the Developers.


##Usage

With a small convenient bash script `gce` like this:

    #!/bin/bash

    echo $*

    gcutil --authorization_uri_base=https://localhost:5000/oauth2 --auth_host_name=127.0.0.1 --auth_host_port=9999 --auth_local_webserver=true --api_host="https://localhost:5000/" --fetch_discovery=true $*

You can start issuing standard gcutil commands. For illustration purposes we use [Exoscale](http://exoscale.ch)

    $ gce --project toto listzones
    --project toto listzones
    +--------+-------------+--------+-------------+-------------------------+-----------------+------------+-------------+----------------------+
    |  name  | description | status | deprecation | next-maintenance-window | instances-usage | cpus-usage | disks-usage | disks-total-gb-usage |
    +--------+-------------+--------+-------------+-------------------------+-----------------+------------+-------------+----------------------+
    | CH-GV2 | CH-GV2      | UP     |             | None scheduled          |                 |            |             |                      |
    +--------+-------------+--------+-------------+-------------------------+-----------------+------------+-------------+----------------------+
    $ gce --project toto listmachinetypes
    --project toto listmachinetypes

    Items in zone/CH-GV2:

    +-------------+--------------------------+--------+------+-----------+----------------------+---------+----------------------+-------------+
    |    name     |       description        |  zone  | cpus | memory-mb | scratch-disk-size-gb | max-pds | max-total-pd-size-gb | deprecation |
    +-------------+--------------------------+--------+------+-----------+----------------------+---------+----------------------+-------------+
    | Micro       | Micro 512mb 1cpu         | CH-GV2 | 1    | 512       |                      |         |                      |             |
    | Tiny        | Tiny 1024mb 1cpu         | CH-GV2 | 1    | 1024      |                      |         |                      |             |
    | Small       | Small 2048mb 2cpu        | CH-GV2 | 2    | 2048      |                      |         |                      |             |
    | Medium      | Medium 4096mb 2cpu       | CH-GV2 | 2    | 4096      |                      |         |                      |             |
    | Large       | Large 8192mb 4cpu        | CH-GV2 | 4    | 8182      |                      |         |                      |             |
    | Extra-large | Extra-large 16384mb 4cpu | CH-GV2 | 4    | 16384     |                      |         |                      |             |
    | Huge        | Huge 32184mb 8cpu        | CH-GV2 | 8    | 32184     |                      |         |                      |             |
    +-------------+--------------------------+--------+------+-----------+----------------------+---------+----------------------+-------------+

	$ gce --project toto listimages
	--project toto listimages
	+---------------------------------+------------------------------------------+--------+-------------+--------+
	|              name               |               description                | kernel | deprecation | status |
	+---------------------------------+------------------------------------------+--------+-------------+--------+
	| CentOS 5.5(64-bit) no GUI (KVM) | CentOS 5.5(64-bit) no GUI (KVM)          |        |             | Ready  |
	| Linux CentOS 6.4 64-bit         | Linux CentOS 6.4 64-bit 10GB Disk        |        |             | Ready  |
	| Linux CentOS 6.4 64-bit         | Linux CentOS 6.4 64-bit 50GB Disk        |        |             | Ready  |
	| Linux CentOS 6.4 64-bit         | Linux CentOS 6.4 64-bit 100GB Disk       |        |             | Ready  |
	| Linux CentOS 6.4 64-bit         | Linux CentOS 6.4 64-bit 200GB Disk       |        |             | Ready  |
	| Linux CentOS 6.4 64-bit         | Linux CentOS 6.4 64-bit 400GB Disk       |        |             | Ready  |
	| Linux Ubuntu 12.04 LTS 64-bit   | Linux Ubuntu 12.04 LTS 64-bit 10GB Disk  |        |             | Ready  |
	| Linux Ubuntu 12.04 LTS 64-bit   | Linux Ubuntu 12.04 LTS 64-bit 50GB Disk  |        |             | Ready  |
	| Linux Ubuntu 12.04 LTS 64-bit   | Linux Ubuntu 12.04 LTS 64-bit 100GB Disk |        |             | Ready  |
	| Linux Ubuntu 12.04 LTS 64-bit   | Linux Ubuntu 12.04 LTS 64-bit 200GB Disk |        |             | Ready  |
	| Linux Ubuntu 12.04 LTS 64-bit   | Linux Ubuntu 12.04 LTS 64-bit 400GB Disk |        |             | Ready  |
	| Linux Ubuntu 13.04 64-bit       | Linux Ubuntu 13.04 64-bit 10 GB Disk     |        |             | Ready  |
	| Linux Ubuntu 13.04 64-bit       | Linux Ubuntu 13.04 64-bit 50 GB Disk     |        |             | Ready  |
	| Linux Ubuntu 13.04 64-bit       | Linux Ubuntu 13.04 64-bit 100 GB Disk    |        |             | Ready  |
	| Linux Ubuntu 13.04 64-bit       | Linux Ubuntu 13.04 64-bit 200 GB Disk    |        |             | Ready  |
	| Linux Ubuntu 13.04 64-bit       | Linux Ubuntu 13.04 64-bit 400 GB Disk    |        |             | Ready  |
	| Windows Server 2008 R2 SP1      | 50                                       |        |             | Ready  |
	| Windows Server 2008 R2 SP1      | Windows Server 2008 R2 SP1 100GB Disk    |        |             | Ready  |
	| Windows Server 2008 R2 SP1      | Windows Server 2008 R2 SP1 200GB Disk    |        |             | Ready  |
	| Windows Server 2008 R2 SP1      | Windows Server 2008 R2 SP1 400GB Disk    |        |             | Ready  |
	| Windows Server 2012             | Windows Server 2012 Disk 50GB            |        |             | Ready  |
	| Windows Server 2012             | Windows Server 2012 Disk 200GB           |        |             | Ready  |
	| Windows Server 2012             | Windows Server 2012 Disk 100GB           |        |             | Ready  |
	| Windows Server 2012             | Windows Server 2012 Disk 400GB           |        |             | Ready  |
	+---------------------------------+------------------------------------------+--------+-------------+--------+
	
To create a securitygroup, use the firewall commands:

    $ gce --project toto listfirewalls
    --project toto listfirewalls
    +---------+------------------------+---------+---------------------+-------------+-------------+
    |  name   |      description       | network |     source-ips      | source-tags | target-tags |
    +---------+------------------------+---------+---------------------+-------------+-------------+
    | default | Default Security Group |         | 0.0.0.0/0,0.0.0.0/0 |             |             |
    +---------+------------------------+---------+---------------------+-------------+-------------+

    $ gce --project toto addfirewall foobar --allowed=tcp:22 --allowed_ip_sources=0.0.0.0/0 --description=test
    --project toto addfirewall foobar --allowed=tcp:22 --allowed_ip_sources=0.0.0.0/0 --description=test
    
	$ gce --project toto listfirewalls
    --project toto listfirewalls
    +---------+------------------------+---------+---------------------+-------------+-------------+
    |  name   |      description       | network |     source-ips      | source-tags | target-tags |
    +---------+------------------------+---------+---------------------+-------------+-------------+
    | default | Default Security Group |         | 0.0.0.0/0,0.0.0.0/0 |             |             |
    | foobar  | test                   |         | 0.0.0.0/0           |             |             |
    +---------+------------------------+---------+---------------------+-------------+-------------+

    $ gce --project toto getfirewall foobar
    --project toto getfirewall foobar
    +---------------+-----------+
    |   property    |   value   |
    +---------------+-----------+
    | name          | foobar    |
    | description   | test      |
    | creation-time |           |
    | network       |           |
    | source-ips    | 0.0.0.0/0 |
    | source-tags   |           |
    | target-tags   |           |
    | allowed       | tcp: 22   |
    +---------------+-----------+

	$ gce --project toto deletefirewall foobar
	--project toto deletefirewall foobar
	Delete firewall foobar? [y/n]
	>>> y
	+------+-------------+---------+------------+-------------+-------------+
	| name | description | network | source-ips | source-tags | target-tags |
	+------+-------------+---------+------------+-------------+-------------+
	|      |             |         |            |             |             |
	+------+-------------+---------+------------+-------------+-------------+
	sebimac:bin sebgoa$ gce --project toto listfirewalls
	--project toto listfirewalls
	+---------+------------------------+---------+---------------------+-------------+-------------+
	|  name   |      description       | network |     source-ips      | source-tags | target-tags |
	+---------+------------------------+---------+---------------------+-------------+-------------+
	| default | Default Security Group |         | 0.0.0.0/0,0.0.0.0/0 |             |             |
	+---------+------------------------+---------+---------------------+-------------+-------------+

To start an instance note that you need to pass your email as project. This is one of the caveat due to semantic differences between projects and domains. Still a work in progress. Feedback and contributions welcome. Also note that persistent disks are not supported yet.

    $ gce --project runseb@gmail.com addinstance foobar
    --project runseb@gmail.com addinstance foobar
    Selecting the only available zone: CH-GV2
    1: Extra-large	Extra-large 16384mb 4cpu
    2: Huge	Huge 32184mb 8cpu
    3: Large	Large 8192mb 4cpu
    4: Medium	Medium 4096mb 2cpu
    5: Micro	Micro 512mb 1cpu
    6: Small	Small 2048mb 2cpu
    7: Tiny	Tiny 1024mb 1cpu
    >>> 7
    The boot disk is unspecified.  I can create a new persistent boot disk and use it (preferred), or use a scratch disk (not recommended).  Do you want to use a persistent boot disk? [y/n]
    >>> n
    1: CentOS 5.5(64-bit) no GUI (KVM)
    2: Linux CentOS 6.4 64-bit
    3: Linux CentOS 6.4 64-bit
    4: Linux CentOS 6.4 64-bit
    5: Linux CentOS 6.4 64-bit
    6: Linux CentOS 6.4 64-bit
    7: Linux Ubuntu 12.04 LTS 64-bit
    8: Linux Ubuntu 12.04 LTS 64-bit
    9: Linux Ubuntu 12.04 LTS 64-bit
    10: Linux Ubuntu 12.04 LTS 64-bit
    11: Linux Ubuntu 12.04 LTS 64-bit
    12: Linux Ubuntu 13.04 64-bit
    13: Linux Ubuntu 13.04 64-bit
    14: Linux Ubuntu 13.04 64-bit
    15: Linux Ubuntu 13.04 64-bit
    16: Linux Ubuntu 13.04 64-bit
    17: Windows Server 2008 R2 SP1
    18: Windows Server 2008 R2 SP1
    19: Windows Server 2008 R2 SP1
    20: Windows Server 2008 R2 SP1
    21: Windows Server 2012
    22: Windows Server 2012
    23: Windows Server 2012
    24: Windows Server 2012
    >>> 7
    INFO: Waiting for insert of instance . Sleeping for 3s.
    INFO: Waiting for insert of instance . Sleeping for 3s.
    INFO: Waiting for insert of instance . Sleeping for 3s.
    INFO: Waiting for insert of instance . Sleeping for 3s.
    INFO: Waiting for insert of instance . Sleeping for 3s.

    Table of resources:

    +--------+--------------+-------------------------------+--------+--------------+-------------+-------------+-------+--------+---------+----------------+
    |  name  | machine-type |             image             | kernel |   network    | network-ip  | external-ip | disks |  zone  | status  | status-message |
    +--------+--------------+-------------------------------+--------+--------------+-------------+-------------+-------+--------+---------+----------------+
    | foobar | Tiny         | Linux Ubuntu 12.04 LTS 64-bit |        | tobereviewed | 185.19.28.6 |             |       | CH-GV2 | RUNNING |                |
    +--------+--------------+-------------------------------+--------+--------------+-------------+-------------+-------+--------+---------+----------------+

    Table of operations:

    +--------------------------------------+--------+--------+--------+----------------+--------+--------------------------+----------------+-------+---------------+---------+
    |                 name                 | region |  zone  | status | status-message | target |       insert-time        | operation-type | error | error-message | warning |
    +--------------------------------------+--------+--------+--------+----------------+--------+--------------------------+----------------+-------+---------------+---------+
    | 781114e4-6dda-4671-989e-aa1bc06d2034 |        | CH-GV2 | DONE   |                | foobar | 2013-09-24T13:38:02+0200 | insert         |       |               |         |
    +--------------------------------------+--------+--------+--------+----------------+--------+--------------------------+----------------+-------+---------------+---------+

You can of course list and delete instances

    $ gce --project runseb@gmail.com listinstances
    --project runseb@gmail.com listinstances


    Items in zone/CH-GV2:

    +--------+--------------+-------------------------------+--------+--------------+-------------+-------------+-------+--------+---------+----------------+
    |  name  | machine-type |             image             | kernel |   network    | network-ip  | external-ip | disks |  zone  | status  | status-message |
    +--------+--------------+-------------------------------+--------+--------------+-------------+-------------+-------+--------+---------+----------------+
    | foobar | Tiny         | Linux Ubuntu 12.04 LTS 64-bit |        | tobereviewed | 185.19.28.6 |             |       | CH-GV2 | RUNNING |                |
    +--------+--------------+-------------------------------+--------+--------------+-------------+-------------+-------+--------+---------+----------------+

    $ gce --project runseb@gmail.com deleteinstance foobar
    --project runseb@gmail.com deleteinstance foobar
    Delete instance foobar? [y/n]
    >>> y
    WARNING: Consider passing '--zone=CH-GV2' to avoid the unnecessary zone lookup which requires extra API calls.
    INFO: Waiting for delete of instance . Sleeping for 3s.
    +--------------------------------------+--------+--------+--------+----------------+-------------------------+--------------------------+----------------+-------+---------------+---------+
    |                 name                 | region |  zone  | status | status-message |         target          |       insert-time        | operation-type | error | error-message | warning |
    +--------------------------------------+--------+--------+--------+----------------+-------------------------+--------------------------+----------------+-------+---------------+---------+
    | c9793c52-17d7-4f20-85cf-faf6b82a6e9a |        | CH-GV2 | DONE   |                | CH-GV2/instances/foobar | 2013-09-24T13:42:13+0200 | delete         |       |               |         |
    +--------------------------------------+--------+--------+--------+----------------+-------------------------+--------------------------+----------------+-------+---------------+---------+

Specification of keypairs and securitygroups via gcutil is still being worked on

##Trouble shooting

If you encounter authentication/authorization issues, clean up your gcutil authentication information `rm -rf ~/.gcutil_auth`, make sure that you set your `client_id` and `client_secret` in `gcutil/lib/google_compute_engine/gcutil/auth_helper.py`

##Apache CloudStack

For more information about CloudStack check the official [website](http://cloudstack.apache.org)

Copyright © 2013 The Apache Software Foundation, Licensed under the Apache License, Version 2.0. 
"Apache", "CloudStack", "Apache CloudStack", and the Apache feather logos are registered trademarks or trademarks of The Apache Software Foundation.
