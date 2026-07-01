{{/*
ConfigMap 한 장을 통째로 찍는 공통 템플릿.
호출한 앱의 컨텍스트(.Values·.Release·.Chart)를 그대로 쓴다.
*/}}
{{- define "common.configmap" -}}
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Release.Name }}-config
  labels:
    {{- include "common.labels" . | nindent 4 }}
data:
  {{- toYaml .Values.config | nindent 2 }}
{{- end -}}
