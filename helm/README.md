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
| 6 | [템플릿 엔진 — 값이 어떻게 매니페스트로 펼쳐지는가](./6-템플릿-엔진) | 값이 어떻게 매니페스트로 펼쳐지는가? | .Values · .Release · .Chart, 파이프 · 함수(default·quote·toYaml·nindent), 공백 제어 |
| 7 | [렌더 디버깅 — 적용 전에 결과를 눈으로 확인하기](./7-렌더-디버깅) | 클러스터에 적용하기 전에 렌더 결과를 어떻게 눈으로 확인하는가? | helm template · --dry-run=server · get manifest, --debug · -s |
| 8 | [변경 비교 — helm diff upgrade](./8-변경-비교-helm-diff) | upgrade하면 실제로 무엇이 바뀌는가? | helm-diff plugin, diff upgrade · diff revision, -/+ 미리보기 |
| 9 | [흐름 제어 — 조건·반복을 템플릿에서 표현하기](./9-흐름-제어) | 조건·반복을 템플릿에서 어떻게 표현하는가? | if · range · with · 변수 · $, 객체 토글 |
| 10 | [named template과 _helpers.tpl — 반복 블록을 재사용하기](./10-named-template과-helpers) | 반복되는 블록을 어떻게 재사용하는가? | define · include · tpl, 컨텍스트 ., 이름·라벨 규칙 |
| 11 | [내 매니페스트를 chart로 — raw를 동작하는 chart로 옮기기](./11-내-매니페스트를-chart로) | 이미 있는 Deployment·Service·ConfigMap·Ingress를 어떻게 chart로 옮기는가? | 값 추출 · _helpers · if/range, values 오버레이, helm test |
| 12 | [Helm vs Kubernetes 경계 — 어디까지 Helm이고 어디부터 k8s인가](./12-Helm-vs-Kubernetes-경계) | 어디까지 Helm 책임이고 어디부터 k8s 책임인가? | manifest 제출 vs rollout, deployed≠health, reconcile은 k8s, --atomic |
