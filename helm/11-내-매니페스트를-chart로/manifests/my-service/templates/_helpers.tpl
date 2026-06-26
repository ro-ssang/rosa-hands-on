{{- define "my-service.fullname" -}}
{{- default .Release.Name .Values.fullnameOverride -}}
{{- end -}}

{{- define "my-service.labels" -}}
app.kubernetes.io/name: my-service
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}

{{- define "my-service.selectorLabels" -}}
app.kubernetes.io/name: my-service
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
