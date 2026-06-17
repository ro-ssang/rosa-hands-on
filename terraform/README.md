# Terraform

## 시리즈

| # | 주제 | 질문 | 주요 컴포넌트 |
|---|---|---|---|
| 0 | [AWS 프로필 준비](./0-AWS-프로필-준비) | AWS 환경을 어떻게 준비하는가? | IAM 사용자, Access key, AWS CLI, 프로필 |
| 1 | [`terraform apply` 한 줄에서 리소스까지](./1-terraform-apply에서-리소스까지) | 코드가 어떻게 실제 리소스가 되는가? | provider, resource, plan, apply, state, destroy |
| 2 | [HCL 한 권](./2-HCL-한-권) | HCL을 어떻게 더 깔끔하고 재사용 가능하게 짜는가? | variable, output, locals, count, for_each |
| 3 | [처음 만나는 AWS](./3-처음-만나는-AWS) | AWS에 어떻게 처음 접속하는가? | aws provider, profile, data, S3, 비용 습관 |
| 4 | [state는 무엇이고 왜 골치인가](./4-state는-무엇이고-왜-골치인가) | drift와 local state의 한계를 어떻게 다루는가? | state, drift, refresh-only, terraform state, remote backend |
