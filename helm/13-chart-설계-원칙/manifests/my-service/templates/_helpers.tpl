{{/*
이름: chart 이름에서 유도하되, nameOverride로 덮을 수 있다.
*/}}
{{- define "my-service.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
fullname: 객체 이름 접두사. fullnameOverride가 최우선,
없으면 release 이름 + (필요 시) chart 이름을 조합한다.
*/}}
{{- define "my-service.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
helm.sh/chart 라벨 값.
*/}}
{{- define "my-service.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
공통 라벨 — selectorLabels를 포함한다(DRY).
*/}}
{{- define "my-service.labels" -}}
helm.sh/chart: {{ include "my-service.chart" . }}
{{ include "my-service.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
selector 라벨 — Deployment selector와 Service selector가 공유한다.
불변이어야 하므로 name/instance만 둔다.
*/}}
{{- define "my-service.selectorLabels" -}}
app.kubernetes.io/name: {{ include "my-service.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
