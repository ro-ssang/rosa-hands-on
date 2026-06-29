#!/usr/bin/env python3
# frontend -> payment 모양의 trace를 OTLP/HTTP로 Tempo에 보낸다.
# 한 요청 = 한 trace_id. frontend의 root span 아래에 payment의 child span이 달린다
# (child의 parentSpanId = frontend span_id) — 실제 서비스 간 호출에서 traceparent 헤더로
# trace_id가 전파됐을 때 만들어지는 바로 그 모양이다.
# 정상(빠름) 10개, 느린 것 2개, 에러 1개를 보낸다 — 검색·샘플링 시연용.
import json, time, secrets, urllib.request, os

ENDPOINT = os.environ.get("OTLP_HTTP", "http://localhost:4318") + "/v1/traces"


def push(payload):
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req).read()


def trace(front_ms, pay_ms, error=False):
    now = time.time_ns()
    tid = secrets.token_hex(16)   # trace_id: 32 hex
    s1 = secrets.token_hex(8)     # frontend root span_id: 16 hex
    s2 = secrets.token_hex(8)     # payment child span_id
    fe = {"traceId": tid, "spanId": s1, "name": "GET /checkout", "kind": 2,
          "startTimeUnixNano": str(now), "endTimeUnixNano": str(now + front_ms * 10**6)}
    pay = {"traceId": tid, "spanId": s2, "parentSpanId": s1, "name": "charge card", "kind": 3,
           "startTimeUnixNano": str(now + 5 * 10**6),
           "endTimeUnixNano": str(now + 5 * 10**6 + pay_ms * 10**6),
           "attributes": [{"key": "http.status_code",
                           "value": {"intValue": 500 if error else 200}}]}
    if error:
        fe["status"] = {"code": 2}
        pay["status"] = {"code": 2}
    return {"resourceSpans": [
        {"resource": {"attributes": [{"key": "service.name", "value": {"stringValue": "frontend"}}]},
         "scopeSpans": [{"spans": [fe]}]},
        {"resource": {"attributes": [{"key": "service.name", "value": {"stringValue": "payment"}}]},
         "scopeSpans": [{"spans": [pay]}]},
    ]}


for _ in range(10):
    push(trace(40, 30))        # 정상 · 빠름
for _ in range(2):
    push(trace(320, 300))      # 느림
push(trace(120, 90, error=True))  # 에러
print("pushed 13 frontend->payment traces (10 fast, 2 slow, 1 error)")
