.PHONY: up demo down clean help

CLUSTER_NAME ?= rosa-lab
KIND_CONFIG ?=

help:
	@echo "Targets:"
	@echo "  make up    - kind 클러스터 생성 + manifests 적용"
	@echo "  make demo  - 시연 실행 (README의 '데모' 섹션 참고)"
	@echo "  make down  - 클러스터 삭제"
	@echo "  make clean - manifests 만 삭제 (클러스터 유지)"

up:
	@if ! kind get clusters | grep -q "^$(CLUSTER_NAME)$$"; then \
		kind create cluster --name $(CLUSTER_NAME) $(if $(KIND_CONFIG),--config $(KIND_CONFIG),); \
	fi
	kubectl apply -f manifests/

demo:
	@echo "데모 단계는 README의 '빠른 시작' 또는 '데모' 섹션 참고."

clean:
	-kubectl delete -f manifests/

down:
	kind delete cluster --name $(CLUSTER_NAME)
