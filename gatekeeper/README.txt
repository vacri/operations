Gatekeeper
==========

What is it?
-----------

It's a deployment system for 'website packages', to assist with CI deployment to autoscaled server farms. It's a very, very crap replica of an apt repo. The tech lead at the time it was written was wholeheartedly against running our own apt repo, but I still needed something to deploy packages to an autoscaled group.

Originally it was used to deploy nodejs packages, but this was in the prehistoric time when docker hadn't ridden to node's rescue yet, well before fun like leftpad, the iojs fork, and advertising running rampant in npm. It later found new life as a php deployer.

Should I use it?
----------------

Probably not. It's heavily unmaintained and has a few warts. It's worked fine for me for close on a decade, but I can't in good conscience recommend it. If you need a php deployer, perhaps use Capistrano?

How does it work?
-----------------

It uses s3 to store an index file of packages and also the packages themselves. The 'indexer' script deals with uploading the packages and updating the index file.

The CI system then deploys by finding the appropriately-tagged VMs, sshing in, and running the deploy script twice. The first run reads the index file and preps the system by pulling the package file and installing it, and the second run activates the new package by switching a symlink. It's broken into two parts this way so that the actual active deployment is a single atomic action for each server.

Why did it stop being used?
---------------------------

The company I worked for moved to docker orchestration and every webisite ran as its own docker service. Packaging was now done via docker rather than tarfiles. The old legacy servers kept using this script, but it gets slow once you have several gigabytes of data to pull - an autoscaling group adds a VM, the bootscripts run gatekeeper to populate the new node, and when there's a lot of data, that takes a while to pull and untar. The system isn't ready for healthchecks until the whole thing is run (well, the way I sorted out the boot), and it was approaching 5 minutes to get a new node up and running - not very good for the traffic spikes we had to deal with.

Why is it called Gatekeeper?
----------------------------

Things need names, that's pretty much the sum of it.
