{{- define "reuse.fullname" -}}
{{ .Release.Name }}-reuse
{{- end -}}

{{- define "reuse.labels" -}}
app.kubernetes.io/name: reuse
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}

{{- define "reuse.selectorLabels" -}}
app.kubernetes.io/name: reuse
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
