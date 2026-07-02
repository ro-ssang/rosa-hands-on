# EKS

Terraform(인프라)과 Kubernetes(워크로드) 사이의 이음매 — AWS 관리형 Kubernetes만의 고유 지점(책임 분담 · Access Entry · IRSA · VPC CNI · 노드 전략 · 애드온 · 업그레이드 · 비용)을 다룹니다.

## 시리즈

| # | 주제 | 질문 |
|---|---|---|
| 1 | [왜 EKS인가](./1-왜-EKS인가) | self-managed k8s 대비 AWS는 무엇을 대신 맡는가? (관리형 control plane, eksctl vs Terraform) |
| 2 | [control plane vs data plane](./2-control-plane-vs-data-plane) | 어디까지 AWS 책임이고 어디부터 내 책임인가? |
| 3 | [클러스터 생성 — Terraform](./3-클러스터-생성-Terraform) | EKS 하나를 띄우면 실제로 무엇이 만들어지는가? (cluster·IAM role·SG·OIDC·node group) |
| 4 | [클러스터 접근 제어](./4-클러스터-접근-제어) | 누가 클러스터에 들어올 수 있는가? (kubeconfig·IAM→Access Entry→RBAC·break-glass) |
| 5 | [node group](./5-node-group) | 노드를 어떻게 띄우는가? (managed node group vs self-managed vs Fargate) |
| 6 | [Karpenter](./6-Karpenter) | 노드를 누가 자동으로 늘리는가? (Karpenter vs Cluster Autoscaler·consolidation) |
| 7 | [인스턴스 전략](./7-인스턴스-전략) | 비용을 어떻게 줄이는가? (spot·타입 다양화·right-sizing·interruption 처리) |

## 고정값

| 항목 | 값 |
|---|---|
| AWS 프로필 | `rosa-lab` |
| 리전 | `ap-northeast-2` (서울) |
| 클러스터 이름 | `rosa-lab` |
| IaC | Terraform (`terraform-aws-eks` 모듈 중심) |

## 전제

- terraform 시리즈 — VPC · IAM · 모듈 · remote state
- kubernetes 시리즈 — 워크로드 전반(Deployment · Service · PV/PVC · HPA · 스케줄링 · NetworkPolicy)
