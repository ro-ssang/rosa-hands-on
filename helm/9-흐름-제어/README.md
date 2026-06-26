# 9. 흐름 제어 — 조건·반복을 템플릿에서 표현하기

값 하나를 가져와 다듬어 박는 표현식만으로는 부족할 때가 있습니다. "이 값이 켜져 있으면 이 객체를 만들어라", "리스트의 항목마다 한 줄씩 찍어라" 같은 논리가 필요합니다. 이 편은 템플릿에 논리를 넣는 네 가지 구문을 봅니다 — **`if`**(조건 분기), **`range`**(리스트·맵 반복), **`with`**(스코프 좁히기), **`$`**(루트 접근). 그리고 `range`·`with` 안에서 `.`이 바뀌기 때문에 생기는 함정 — 최상위 객체를 `$`로 가져와야 하는 이유 — 까지 직접 확인합니다. 결과가 눈에 보이도록 ConfigMap의 `data`로 찍습니다. 산출물은 흐름 제어 시연 chart `flow/`와, 각 구문이 무엇을 만들어내는지 렌더로 본 기록입니다.

## 핵심 다이어그램

```mermaid
flowchart TB
    IF["if / else\n조건으로 줄·블록·객체를 켜고 끔"]
    RANGE["range\n리스트·맵을 돌며 반복"]
    WITH["with\n스코프를 하위 객체로 좁힘"]
    DOLLAR["$\nrange·with 안에서 루트 접근"]
```

```mermaid
flowchart LR
    A["바깥\n. = 루트 (.Release · .Values …)"]
    B["range · with 안\n. = 원소 · 좁힌 객체"]
    C["루트가 필요하면\n$ 로 접근"]
    A --> B --> C
```

- **if는 분기다.** `{{ if cond }}…{{ else }}…{{ end }}`. 값 하나로 한 줄을, 블록을, 심지어 객체 전체를 켜고 끕니다.
- **range는 반복이다.** 리스트나 맵을 돌며 같은 틀을 항목마다 찍습니다. `$i, $e`(인덱스·원소) 또는 `$k, $v`(키·값)로 받습니다.
- **with는 스코프를 좁힌다.** `{{ with .Values.config }}` 안에서는 `.`이 `.Values.config`를 가리켜, `.host`처럼 짧게 씁니다.
- **루트는 $다.** `range`·`with` 안에서 `.`이 원소로 바뀌므로, 최상위(`.Release`·`.Values` 등)는 `$`로 접근해야 합니다.

아래 시연이 이 구문들을 한 줄씩 손으로 확인합니다.

## 사전 준비물

이 실습은 **macOS** 환경을 기준으로 합니다. 이 편은 `helm template`으로 렌더만 하므로 클러스터·namespace는 필요 없습니다.

- **Homebrew** — macOS 패키지 관리자.

### Helm v3 설치

이 시리즈는 **Helm v3** 기준입니다. Homebrew가 v4를 설치한다면, 아래로 v3 바이너리를 받습니다 (Intel Mac은 `arm64`를 `amd64`로 바꿉니다).

```bash
brew install helm
helm version --short      # v3.x.x 인지 확인

# v4가 깔렸다면 v3로 교체
curl -fsSL https://get.helm.sh/helm-v3.21.2-darwin-arm64.tar.gz -o /tmp/helm3.tgz
tar -xzf /tmp/helm3.tgz -C /tmp
sudo mv /tmp/darwin-arm64/helm /usr/local/bin/helm
helm version --short      # v3.21.2
```

## 실습 환경

| 파일 | 내용 |
|---|---|
| `manifests/flow/` | 흐름 제어 시연 chart (`templates/configmap.yaml` + `templates/feature.yaml`) |

`values.yaml`은 조건·리스트·맵·중첩 객체를 한 벌 담습니다.

```yaml
featureEnabled: true
env:
  - name: LOG_LEVEL
    value: info
  - name: REGION
    value: ap-northeast-2
labels:
  team: platform
  tier: backend
config:
  host: example.com
  port: 8080
```

아래 명령은 `manifests/` 디렉터리에서 실행합니다.

```bash
cd manifests
```

## 여기서 직접 확인할 수 있는 것

### 네 구문을 한 ConfigMap에 — 템플릿과 렌더

`templates/configmap.yaml`이 네 구문을 한꺼번에 씁니다.

```yaml
data:
  # if / else — 조건에 따라 다른 값
  mode: {{ if .Values.featureEnabled }}enabled{{ else }}disabled{{ end }}
  # range over list — 인덱스와 원소
  {{- range $i, $e := .Values.env }}
  env-{{ $i }}: {{ $e.name }}={{ $e.value }}
  {{- end }}
  # range over map — 키와 값
  {{- range $k, $v := .Values.labels }}
  label-{{ $k }}: {{ $v }}
  {{- end }}
  # with — 스코프를 .Values.config 로 좁힘
  {{- with .Values.config }}
  endpoint: {{ .host }}:{{ .port }}
  {{- end }}
  # range 안에서 . 는 원소다 → 루트는 $ 로 접근
  {{- range .Values.env }}
  {{ $.Release.Name }}-{{ .name }}: {{ .value }}
  {{- end }}
```

렌더하면 각 구문이 무엇을 찍는지 드러납니다.

```bash
helm template app flow -s templates/configmap.yaml
```

```yaml
---
# Source: flow/templates/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-flow
data:
  # if / else — 조건에 따라 다른 값
  mode: enabled
  # range over list — 인덱스와 원소
  env-0: LOG_LEVEL=info
  env-1: REGION=ap-northeast-2
  # range over map — 키와 값
  label-team: platform
  label-tier: backend
  # with — 스코프를 .Values.config 로 좁힘
  endpoint: example.com:8080
  # range 안에서 . 는 원소다 → 루트는 $ 로 접근
  app-LOG_LEVEL: info
  app-REGION: ap-northeast-2
```

- **if** — `featureEnabled: true`라 `mode: enabled`. else 쪽은 쓰이지 않았습니다.
- **range(list)** — `env` 두 항목이 `env-0`·`env-1`로. `$i`가 인덱스(0,1), `$e`가 원소(map)라 `$e.name`·`$e.value`를 꺼냈습니다.
- **range(map)** — `labels`의 키·값이 `label-team`·`label-tier`로. `$k`가 키, `$v`가 값입니다.
- **with** — `endpoint`가 `.host`·`.port`만으로 채워졌습니다. `with .Values.config` 덕에 `.Values.config.host`를 `.host`로 짧게 썼습니다.
- **$** — `app-LOG_LEVEL`처럼 `$.Release.Name`(=`app`)이 각 원소 이름과 합쳐졌습니다.

### if — 객체 전체를 켜고 끈다

`if`는 한 줄만이 아니라 매니페스트 하나를 통째로 감쌀 수 있습니다. `templates/feature.yaml`은 전체가 `{{- if .Values.featureEnabled }}`로 감싸여 있습니다.

```yaml
{{- if .Values.featureEnabled }}
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Release.Name }}-feature
data:
  note: "feature is on"
{{- end }}
```

기본값(`featureEnabled: true`)에서는 ConfigMap이 둘 렌더됩니다 — `app-flow`와 `app-feature`.

```bash
helm template app flow | grep -E '^kind:|name: '
```

```
kind: ConfigMap
  name: app-flow
kind: ConfigMap
  name: app-feature
```

값을 끄면 `mode`가 `disabled`로 바뀌고, `feature.yaml`은 한 줄도 렌더되지 않아 ConfigMap이 하나만 남습니다.

```bash
helm template app flow --set featureEnabled=false | grep -E '^kind:|mode:'
```

```
kind: ConfigMap
  mode: disabled
```

값 하나가 매니페스트 하나를 통째로 켜고 끄는 것은, 이렇게 객체 전체를 `{{ if }}`로 감쌌기 때문입니다.

### $ — range 안에서 루트에 닿는 법

`range` 블록 안에서는 `.`이 현재 원소를 가리킵니다. 그래서 그 안에서 `.Release.Name`을 쓰면 "원소(map)에 `.Release`가 없다"며 깨집니다. 위 템플릿의 `$.Release.Name`을 `.Release.Name`으로 바꿔 확인합니다.

```bash
cp -r flow /tmp/flow-bad
sed -i '' 's/{{ \$\.Release\.Name }}/{{ .Release.Name }}/' /tmp/flow-bad/templates/configmap.yaml
helm template app /tmp/flow-bad
rm -rf /tmp/flow-bad
```

```
Error: template: flow/templates/configmap.yaml:22:13: executing "flow/templates/configmap.yaml" at <.Release.Name>: nil pointer evaluating interface {}.Name
```

`<.Release.Name> ... nil pointer` — `range` 안의 `.`은 `env`의 원소라 `.Release`가 없어서 난 에러입니다. 루트는 `range` 진입 전에 `$`로 묶여 있으므로, 그 안에서도 `$.Release.Name`으로 닿을 수 있습니다(`{{ $name := .Release.Name }}`처럼 변수로 미리 잡아 두는 방법도 같은 해법입니다).

### 정리

이 편은 렌더만 했으므로 따로 정리할 것이 없습니다(`$` 확인에서 만든 `/tmp/flow-bad`는 마지막 줄에서 지웁니다).

## 이 편의 산출물

- 흐름 제어 시연 chart `flow/`와, `if`·`range`·`with`·`$` 네 구문이 한 ConfigMap에서 무엇을 찍는지 렌더로 본 기록.
- `if`로 값(`mode`)을 분기하고 `feature.yaml`처럼 **객체 전체를 켜고 끄는** 것을 `--set featureEnabled=false`로 확인한 경험.
- `range`가 리스트(`$i, $e` — 인덱스·원소)와 맵(`$k, $v` — 키·값)을 도는 두 형태를 구분한 상태.
- `with`로 스코프를 하위 객체로 좁혀 `.host`처럼 짧게 쓰는 법을 본 상태.
- `range` 안에서 `.`이 원소로 바뀌어 `.Release.Name`이 `nil pointer`로 깨지는 것을 재현하고, 루트는 `$`로 접근한다는 규칙을 확인한 경험.
