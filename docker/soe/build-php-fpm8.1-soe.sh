#!/bin/bash
set -euo pipefail

version=8.1

image="php$version"
src_dir="php-fpm${version}-soe"
remote_public=public.ecr.aws/MY_AWS_ECR_NICKNAME
timestamp=$(date +%Y%m%d%H%M%S)

cd $src_dir
docker image build --pull -t $image .
docker tag $image:latest $remote_public/$image:latest
docker tag $image:latest $remote_public/$image:$timestamp

echo "To push up to ECR, please do both:"
echo "  docker push $remote_public/$image:latest"
echo "  docker push $remote_public/$image:$timestamp"
echo "The image will then be available on $remote_public/$image"
