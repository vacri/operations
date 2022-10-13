Dockerfile setups for SOE images
================================

Some docker SOE images I used at Frankly/LKG. The php 8.1 build script is just a sample of how I would build these locally and push them to our SOE repositories in AWS ECR.

Logging into ECR
----------------

* Do an MFA login on the cli (there's a .bashrc snippet to help with this in the ops git repo)
* log into private ECR with `$(aws ecr get-login --no-include-email --region ap-southeast-2)`
* log into public ECR with `aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws`



Size Comparison
---------------

```
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
alpine              latest              b7b28af77ffe        4 days ago          5.58MB    # official Dockerhub image for a super-small image base
debian              buster-slim         2dae943fc808        5 weeks ago         69.2MB    # official Dockerhub image for debian stable, made pretty small
php                 7.3-fpm             45b8856a5d0b        2 weeks ago         367MB     # official Dockerhub php image
php7.3-soe          latest              0c2d275e6c94        5 minutes ago       208MB     # the first working php-fpm-soe in this repo
```

Why is our php image so much smaller than the official image, given it also includes nginx and supervisord - plus both are based on debian-slim?

Well, a couple of reasons. The first is that we support slightly fewer modules by default, so there's simply less active php code in our image. The second is that the official image installs everything via building from source, so it has to install the build dependencies as well... and it doesn't uninstall them after compilation is complete.



php-fpm-soe
-----------

A docker image running 'supervisord' which in turn runs php-fpm and nginx. This allows the two web services to directly access the same filesystem with zero shenanigans. The default nginx config serves on port 8080, but custom config should be added.

This image is tuned for 500MB of allocated memory on AWS ECS - approx 50MB set aside for supervisord and nginx, and 8 php workers *assuming an average of ~50MB each*, with a slop space of about 50MB memory left over.

You can increase the parallel workers by increasing pm.max_children in the fpm config. Alternatively, you could just increase the number of containers in the docker autoscaling group :)

At time of writing (July 2019) this is a PHP7.3 image. Different versions of the image should be put into new, appropriately-named directories. Changing the version of PHP on this image is done by enabling the sury.org repos - see comments inside the Dockerfile for how to do that. You will also need to change the conf file for supervisord

