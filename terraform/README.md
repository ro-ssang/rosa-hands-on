# Terraform

## 시리즈

| # | 주제 | 질문 | 주요 컴포넌트 |
|---|---|---|---|
| 0 | [AWS 프로필 준비](./0-AWS-프로필-준비) | AWS 환경을 어떻게 준비하는가? | IAM 사용자, Access key, AWS CLI, 프로필 |
| 1 | [`terraform apply` 한 줄에서 리소스까지](./1-terraform-apply에서-리소스까지) | 코드가 어떻게 실제 리소스가 되는가? | provider, resource, plan, apply, state, destroy |
| 2 | [HCL 한 권](./2-HCL-한-권) | HCL을 어떻게 더 깔끔하고 재사용 가능하게 짜는가? | variable, output, locals, count, for_each |
| 3 | [처음 만나는 AWS](./3-처음-만나는-AWS) | AWS에 어떻게 처음 접속하는가? | aws provider, profile, data, S3, 비용 습관 |
| 4 | [state는 무엇이고 왜 골치인가](./4-state는-무엇이고-왜-골치인가) | drift와 local state의 한계를 어떻게 다루는가? | state, drift, refresh-only, terraform state, remote backend |
| 5 | [VPC와 친구들](./5-VPC와-친구들) | AWS 네트워킹을 어떻게 코드로 짜는가? | VPC, subnet, IGW, route table, security group |
| 6 | [IAM](./6-IAM) | 권한을 어떻게 코드로 짜고 검증하는가? | policy, role, trust policy, AssumeRole, 최소 권한 |
| 7 | [EC2 한 대 띄우고 SSH까지](./7-EC2-한-대-띄우고-SSH까지) | EC2 한 대를 어떻게 띄우고 들어가는가? | AMI, key pair, user_data, security group, EC2 |
| 8 | [모듈 — 무엇을 떼어내는가](./8-모듈-무엇을-떼어내는가) | 반복되는 인프라를 어떻게 모듈로 떼어내는가? | module, source, input/output, for_each, 버전 핀 |
| 9 | [remote state](./9-remote-state) | state를 어떻게 공용 저장소로 옮기고 동시 작업을 막는가? | backend "s3", use_lockfile, 부트스트랩, init -migrate-state |
| 10 | [리소스 라이프사이클](./10-리소스-라이프사이클) | 리소스의 변경·리네임·기존 자원 편입을 어떻게 다루는가? | in-place vs replace, lifecycle, moved, import |
| 11 | [환경이 둘이 되면 무엇이 깨지는가](./11-환경이-둘이-되면-무엇이-깨지는가) | multi-env로 가면 Terraform만으로는 어디가 부족한가? | workspace, 폴더 분리, backend 중복, terraform.workspace |
