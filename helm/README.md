# Helm

`kubectl apply`로 흩어지는 매니페스트를, **release**라는 한 단위로 패키징·배포·운영하는 법. 처음부터 실무 수준까지.

## 시리즈

| # | 주제 | 질문 | 핵심 |
|---|---|---|---|
| 1 | [왜 Helm인가 — release라는 단위](./1-왜-Helm인가-release라는-단위) | `kubectl apply -f`의 한계는 무엇이고, 매니페스트 묶음을 왜 한 단위로 다루는가? | release, install · upgrade · rollback · uninstall, history |
| 2 | [첫 release — 남의 chart 설치](./2-첫-release-남의-chart-설치) | repo에서 chart를 받아 어떻게 설치하고 상태를 보는가? | repo add · search · show values, install --version -f, get values / manifest |
| 3 | [release 라이프사이클 — upgrade · rollback](./3-release-라이프사이클-upgrade-rollback) | 설치한 release를 어떻게 올리고(upgrade) 되돌리는가(rollback)? | revision · history, rollback, --reuse-values |
| 4 | [Helm 내부 구조 — release는 어디 저장되는가](./4-Helm-내부-구조-release는-어디-저장되는가) | `helm install`이 만든 release 상태는 어디에, 어떤 형태로 저장되는가? | sh.helm.release Secret, base64·gzip 디코드, storage driver |
| 5 | [chart 해부 — chart는 무엇으로 이뤄지는가](./5-chart-해부) | chart는 무엇으로 이뤄지는가? | helm create, Chart.yaml · values.yaml · templates/ · NOTES.txt · _helpers.tpl |
