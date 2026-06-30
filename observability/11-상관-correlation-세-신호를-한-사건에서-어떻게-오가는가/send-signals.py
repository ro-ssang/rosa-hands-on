#!/usr/bin/env python3
# 한 요청마다 두 신호를 같은 trace_id로 심는다:
#   - trace  -> Tempo (frontend -> payment span 트리)
#   - log    -> Loki  (그 요청의 로그 한 줄, 본문에 trace_id 포함)
# 둘 다 service 라벨을 공유하고, trace_id가 둘을 잇는 키다.
# 정상 8개와 에러 1개를 보낸다 — 에러 요청의 trace_id를 출발점으로 신호 사이를 오간다.
import json, time, secrets, urllib.request, os

TEMPO = os.environ.get("OTLP_HTTP", "http://localhost:4318") + "/v1/traces"
LOKI = os.environ.get("LOKI_HTTP", "http://localhost:3100") + "/loki/api/v1/push"


def post(url, payload):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req).read()


def emit(front_ms, pay_ms, error=False):
    now = time.time_ns()
    tid = secrets.token_hex(16)
    s1 = secrets.token_hex(8)   # frontend root span
    s2 = secrets.token_hex(8)   # payment child span
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
    post(TEMPO, {"resourceSpans": [
        {"resource": {"attributes": [{"key": "service.name", "value": {"stringValue": "frontend"}}]},
         "scopeSpans": [{"spans": [fe]}]},
        {"resource": {"attributes": [{"key": "service.name", "value": {"stringValue": "payment"}}]},
         "scopeSpans": [{"spans": [pay]}]},
    ]})
    # 같은 trace_id를 본문에 담은 로그 한 줄 (trace_id는 고카디널리티 -> label이 아니라 content)
    lvl = "error" if error else "info"
    msg = "upstream failed" if error else "request handled"
    code = 500 if error else 200
    line = json.dumps({"level": lvl, "msg": msg, "code": code, "trace_id": tid})
    post(LOKI, {"streams": [{"stream": {"service_name": "checkout"},
                             "values": [[str(now), line]]}]})
    return tid


for _ in range(8):
    emit(40, 30)
terr = emit(120, 90, error=True)
print("에러 요청의 trace_id:", terr)
