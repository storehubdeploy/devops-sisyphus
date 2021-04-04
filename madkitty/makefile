RELEASE_NAME ?= madkitty
NAMESPACE = "utilities"

# Docker part
IMAGE_NAME = "harbor.mymyhub.com/devops/madkitty-api"
IMAGE_TAG = "latest"

build:
	@docker build \
		-t $(IMAGE_NAME):$(IMAGE_TAG) ./image

push:
	# Push to harbor
	docker push $(IMAGE_NAME):$(IMAGE_TAG)


install:
	kubectl create namespace $(NAMESPACE)
	helm upgrade -i $(RELEASE_NAME) ./chart -n $(NAMESPACE)
