###### START CHANGABLE ######

# path to the code
BASE_PATH     := .
# path to the data
DATA_PATH     := ./data

####### END CHANGABLE #######

ABS_BASE_PATH := $$(realpath .)/${BASE_PATH}
IMAGE         := vovacher/ml-contests-cicd:1.0

TIMESTAMP     := $(shell date +%s%N | cut -b1-13)
PORT          := 8$$(echo ${TIMESTAMP} | rev | cut -c -3 | rev)

all:
	@echo "Please specify target!"

evaluate: create evaluator destroy
	@echo "$@ is done!"

create:
	docker pull ${IMAGE}
	AVAILABLE_CORES=$$(nproc); \
	DESIRABLE_CORES=1; \
	CPUS_LIMIT=$$((AVAILABLE_CORES > DESIRABLE_CORES ? DESIRABLE_CORES : AVAILABLE_CORES)); \
	docker run \
		-d \
		-v ${ABS_BASE_PATH}/src:/root/solution/src \
		-v ${ABS_BASE_PATH}/models:/root/solution/models \
		-p ${PORT}:8000 \
		--memory="1g" \
		--cpus=$${CPUS_LIMIT} \
		--name="server-${TIMESTAMP}" \
		${IMAGE} \
		/bin/bash -c "cd /root/solution/src && python3 server.py"

evaluator:
	docker run \
		-v ${ABS_BASE_PATH}/client:/root/solution/client \
		-v ${ABS_BASE_PATH}/data:/root/solution/data \
		--rm \
		--net="host" \
		--name="client-${TIMESTAMP}" \
		${IMAGE} \
		/bin/bash -c "cd /root/solution/client && python3 evaluator.py \
															--folder-path ../${DATA_PATH} \
															--url http://localhost:${PORT}"

destroy:
	mkdir -p logs
	docker logs server-${TIMESTAMP} > logs/logs-${TIMESTAMP} 2>&1
	@if [ `cat logs/logs-${TIMESTAMP} | grep '500 -' | wc -l` -gt 0 ]; \
	then \
		cat logs/logs-${TIMESTAMP}; \
	fi
	@if [ `docker ps -a --filter name=server-${TIMESTAMP} --filter status=exited | wc -l` -gt 1 ]; \
	then \
		cat logs/logs-${TIMESTAMP}; \
	fi
	docker stop server-${TIMESTAMP}
	docker rm server-${TIMESTAMP}

destroy_all:
	docker stop $$(docker ps -aq --filter="name=server-*")
	docker rm $$(docker ps -aq --filter="name=server-*")

build:
	cp dockers/.dockerignore .
	docker build -f dockers/Dockerfile -t vovacher/ml-contests-cicd:1.0 .
	rm .dockerignore

push:
	docker push vovacher/ml-contests-cicd:1.0
