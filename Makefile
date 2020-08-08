DOCKERHUB_USER ?= $(USER)
IMAGE := $(DOCKERHUB_USER)/ping-matrix

build:
	docker build --pull -t $(IMAGE) .

run:
	./server/server.py

run-docker: build
	docker run --rm -p 8000:8000 -it $(IMAGE)
