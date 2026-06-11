.PHONY: shell pull

IMAGE := ubuntu:24.04

pull:
	docker pull $(IMAGE)

shell:
	docker run --privileged --cgroupns=host --rm -it $(IMAGE) bash
