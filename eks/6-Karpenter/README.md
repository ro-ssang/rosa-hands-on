# 6. Karpenter

Pending Pod이 생기면 Karpenter가 그 Pod에 맞는 크기의 노드를 직접 띄우고, 노드가 남으면 consolidation으로 거둡니다. 이 편이 끝나면 노드 autoscaling을 Karpenter로 재현하고 Cluster Autoscaler와 무엇이 다른지 설명할 수 있습니다.

## 핵심 다이어그램

```mermaid
flowchart LR
    P["Pending Pod<br>(어느 노드에도 안 맞음)"]
    K["Karpenter controller<br>(unschedulable Pod 감시)"]
    EC2["EC2 인스턴스<br>Pod에 맞춰 타입·개수 선택"]
    C{"노드가 남는가?"}

    P -->|감지| K
    K -->|프로비저닝| EC2
    EC2 -->|Pod 스케줄| RUN["Running"]
    RUN --> C
    C -->|"비거나 저활용"| DROP["consolidation<br>노드 축소·교체"]
```

- **Cluster Autoscaler** — 미리 정의한 node group(ASG)을 늘리고 줄인다. 어떤 인스턴스 타입을 쓸지는 node group마다 고정돼 있어, 큰 Pod이 와도 그 그룹의 타입으로만 늘린다.
- **Karpenter** — ASG를 거치지 않고 Pending Pod을 직접 보고 **그 Pod에 맞는 인스턴스 타입·개수**를 골라 EC2를 띄운다. 여러 타입·spot을 한 풀에서 고른다.
- **consolidation** — Karpenter가 노드 사용률을 지켜보다 비거나 저활용된 노드의 Pod을 다른 노드로 옮기고 그 노드를 거둔다. bin-packing으로 비용을 조인다.
- **NodePool / EC2NodeClass** — 무엇을 띄울지 정하는 두 리소스. NodePool은 제약(타입·capacity·한도·disruption), EC2NodeClass는 AMI·subnet·SG·노드 IAM role.

## 사전 준비

- **macOS + Homebrew** — `brew install awscli kubernetes-cli terraform helm`
- **AWS 프로필 `rosa-lab`** — 리전 `ap-northeast-2`(서울).

## 빠른 시작

Karpenter는 자신이 관리하지 않는 안정된 자리에서 돌아야 하므로, 작은 managed node group에 Karpenter controller를 두고 나머지 노드는 Karpenter가 띄운다.

```bash
mkdir -p /tmp/eks-lab-6 && cd /tmp/eks-lab-6
```

```hcl
# main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = "ap-northeast-2"
  profile = "rosa-lab"
}

data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  name = "rosa-lab"
  azs  = slice(data.aws_availability_zones.available.names, 0, 2)
  tags = {
    Project = "rosa-hands-on"
    Edition = "eks-6"
  }
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${local.name}-vpc"
  cidr = "10.0.0.0/16"

  azs                     = local.azs
  public_subnets          = ["10.0.1.0/24", "10.0.2.0/24"]
  enable_nat_gateway      = false
  map_public_ip_on_launch = true

  # Karpenter가 subnet을 찾을 discovery 태그
  public_subnet_tags = {
    "karpenter.sh/discovery" = local.name
  }

  tags = local.tags
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = local.name
  cluster_version = "1.32"

  cluster_endpoint_public_access           = true
  enable_cluster_creator_admin_permissions = true

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.public_subnets

  # Karpenter가 security group을 찾을 discovery 태그
  node_security_group_tags = {
    "karpenter.sh/discovery" = local.name
  }

  eks_managed_node_groups = {
    system = {
      instance_types = ["t3.medium"]
      min_size       = 2
      max_size       = 2
      desired_size   = 2
      subnet_ids     = module.vpc.public_subnets
    }
  }

  tags = local.tags
}

# ─── Karpenter용 IAM·SQS ───
module "karpenter" {
  source  = "terraform-aws-modules/eks/aws//modules/karpenter"
  version = "~> 20.0"

  cluster_name = module.eks.cluster_name

  # Pod Identity로 controller 권한을 붙인다(OIDC IRSA 배선 불필요)
  enable_pod_identity             = true
  create_pod_identity_association = true

  # Karpenter 노드가 SSM으로 접근되도록(선택)
  node_iam_role_additional_policies = {
    AmazonSSMManagedInstanceCore = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  }

  tags = local.tags
}

output "karpenter_queue_name" {
  value = module.karpenter.queue_name
}

output "karpenter_node_role_name" {
  value = module.karpenter.node_iam_role_name
}
```

```bash
terraform init
terraform apply   # 약 15분
#   Enter a value: yes

aws eks update-kubeconfig --name rosa-lab --region ap-northeast-2 --profile rosa-lab
```

### Karpenter 설치 (Helm)

```bash
QUEUE=$(terraform output -raw karpenter_queue_name)

helm upgrade --install karpenter oci://public.ecr.aws/karpenter/karpenter \
  --version "1.3.3" \
  --namespace kube-system \
  --set "settings.clusterName=rosa-lab" \
  --set "settings.interruptionQueue=${QUEUE}" \
  --wait
# (버전은 현재 배포된 최신 1.x로 맞춘다)

kubectl -n kube-system get pods -l app.kubernetes.io/name=karpenter
# karpenter-...   1/1   Running
```

### NodePool · EC2NodeClass 적용

Karpenter에게 "무엇을, 어떻게 띄울지" 알려 준다.

```bash
NODE_ROLE=$(terraform output -raw karpenter_node_role_name)

cat <<EOF | kubectl apply -f -
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: default
spec:
  template:
    spec:
      requirements:
        - key: kubernetes.io/arch
          operator: In
          values: ["amd64"]
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["on-demand"]
        - key: node.kubernetes.io/instance-type
          operator: In
          values: ["t3.medium", "t3.large", "t3.xlarge"]
      nodeClassRef:
        group: karpenter.k8s.aws
        kind: EC2NodeClass
        name: default
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    consolidateAfter: 30s
  limits:
    cpu: "10"
---
apiVersion: karpenter.k8s.aws/v1
kind: EC2NodeClass
metadata:
  name: default
spec:
  amiSelectorTerms:
    - alias: al2023@latest
  role: ${NODE_ROLE}
  subnetSelectorTerms:
    - tags:
        karpenter.sh/discovery: rosa-lab
  securityGroupSelectorTerms:
    - tags:
        karpenter.sh/discovery: rosa-lab
EOF
```

## 여기서 직접 확인할 수 있는 것

### Pending Pod이 생기면 노드가 스스로 뜬다

CPU를 요구하는 Pod을 여러 개 만들어 기존 노드를 넘어서게 한다.

```bash
kubectl create deployment inflate \
  --image=public.ecr.aws/eks-distro/kubernetes/pause:3.7 --replicas=0
kubectl set resources deployment inflate --requests=cpu=1
kubectl scale deployment inflate --replicas=5
```

Pod이 기존 노드에 다 안 들어가면 잠시 Pending이 된다.

```bash
kubectl get pods -l app=inflate
# 일부 Pending

# Karpenter가 새 노드를 띄우는 과정을 지켜본다
kubectl get nodes -l karpenter.sh/nodepool -w
# 약 1분 안에 karpenter가 띄운 노드가 Ready로 올라오고 Pending Pod이 스케줄됨
```

Karpenter는 5개의 `cpu=1` Pod을 담기에 맞는 인스턴스 타입을 `t3.medium/large/xlarge` 중에서 골라 **필요한 만큼만** 띄운다. 미리 정한 ASG 크기를 늘리는 방식이 아니다.

```bash
kubectl get nodes -L node.kubernetes.io/instance-type,karpenter.sh/capacity-type
# system 노드(t3.medium) 2대 + karpenter가 띄운 노드(예: t3.xlarge on-demand)
```

### consolidation — 노드가 남으면 거둔다

Pod을 0으로 줄이면 karpenter 노드가 빈다.

```bash
kubectl scale deployment inflate --replicas=0

kubectl get nodes -l karpenter.sh/nodepool -w
# consolidateAfter(30s)가 지나면 빈 karpenter 노드가 사라진다
```

Karpenter 이벤트로 무엇을 했는지 남는다.

```bash
kubectl get events -A --field-selector reason=DisruptionTerminating
# karpenter가 저활용/빈 노드를 종료했다는 이벤트
```

늘 켜져 있는 노드 수를 사람이 정하는 대신, 실제 Pod 수요에 맞춰 노드가 뜨고 지는 것을 눈으로 확인할 수 있다.

### 장애 실험 — 한도(limits)에 걸리면 Pod은 Pending에 멈춘다

NodePool의 `limits.cpu` 는 Karpenter가 이 풀로 띄울 수 있는 CPU 총량이다. 그 위로 밀면 Karpenter는 노드를 더 띄우지 않는다.

```bash
# 한도(cpu 10)를 넘도록 크게 스케일
kubectl scale deployment inflate --replicas=20   # cpu 20 요청 > 한도 10

kubectl get pods -l app=inflate
# 일부만 Running, 나머지는 계속 Pending

# 왜 안 뜨는지 Karpenter가 이유를 남긴다
kubectl describe nodepool default | sed -n '/Resources/,/Events/p'
# Resources: cpu가 한도(10)에 도달 → 더 프로비저닝 안 함
```

한도가 없으면 스케일 실수 하나가 EC2를 무한정 띄운다. NodePool의 `limits` 가 비용의 상한선이다. 실험 뒤 되돌린다.

```bash
kubectl scale deployment inflate --replicas=0
```

### Karpenter vs Cluster Autoscaler

| | Cluster Autoscaler | Karpenter |
|---|---|---|
| 스케일 대상 | 미리 정의한 node group(ASG) | Pending Pod에 맞춘 EC2 직접 |
| 인스턴스 타입 선택 | node group마다 고정 | 여러 타입·spot을 한 풀에서 |
| 반응 속도 | ASG 경유로 느린 편 | 빠른 편(직접 EC2) |
| 비용 최적화 | scale-down 위주 | consolidation(교체·bin-packing) |
| 노드 다양성 | node group 수만큼 관리 | NodePool 하나로 넓게 |

Cluster Autoscaler는 "정해진 그룹을 몇 대로?"를 푼다. Karpenter는 "이 Pod들을 담을 가장 알맞은 노드는?"을 푼다. 후자가 타입 선택·bin-packing에서 유리해 EKS의 기본 선택지로 자리 잡았다.

### 비용 영향

- **control plane** — 약 $0.10/h.
- **system 노드** — `t3.medium` 2대 ≈ $0.10/h(Karpenter controller가 여기 상주).
- **Karpenter가 띄운 노드** — 실험 중에만 존재하고 consolidation으로 사라진다. Pod을 0으로 줄이면 이 비용도 0으로 수렴.
- **SQS interruption queue** — 사실상 무시할 수준.
- **spot** — NodePool의 `capacity-type` 에 `spot` 을 더하면 같은 노드를 크게 싸게 띄운다(중단 감수).
- 유휴 시 합계 대략 **$0.20/h**(system 노드 + control plane).

### 제거 방법

Karpenter가 띄운 노드부터 비운 뒤 지운다.

```bash
kubectl delete deployment inflate
kubectl delete nodepool default
kubectl delete ec2nodeclass default
# karpenter 노드가 모두 사라졌는지 확인
kubectl get nodes -l karpenter.sh/nodepool
# No resources found

helm uninstall karpenter -n kube-system

cd /tmp/eks-lab-6
terraform destroy
#   Enter a value: yes
```

```bash
kubectl config delete-context "$(kubectl config current-context)" 2>/dev/null || true

aws eks list-clusters --region ap-northeast-2 --profile rosa-lab
# { "clusters": [] }
```

### 실습 폴더 정리

```bash
cd ..
rm -rf /tmp/eks-lab-6
```
