#!/bin/bash
#https://github.com/pangeo-data/pangeo-docker-images/blob/master/run_tests.sh

# Usage: docker run -w /home/sagemaker-user/test -v ./test:/home/sagemaker-use/test cropy-v01:latest ./run_tests.sh base-notebook
echo "Testing docker image {$1}..."

# --no-channel-priority added b/c solver failing installing into ml-notebook
conda install pytest --freeze-installed --no-channel-priority

pytest -v test_library.py test_$1.py

#EOF