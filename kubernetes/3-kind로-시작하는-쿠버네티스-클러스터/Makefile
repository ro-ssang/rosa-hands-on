.PHONY: up demo down

up:
	kind create cluster --name rosa-lab

demo:
	kubectl get nodes
	kubectl run my-nginx --image=nginx
	kubectl wait --for=condition=Ready pod/my-nginx --timeout=60s
	kubectl get pods

down:
	kind delete cluster --name rosa-lab
