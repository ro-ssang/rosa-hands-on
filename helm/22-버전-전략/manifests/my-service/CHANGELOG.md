# Changelog

버전 표기는 chart `version` 기준입니다. `appVersion`(패키징한 앱 버전)은 괄호로 따로 적습니다.

## 1.0.0 (appVersion 1.28)

### Changed (breaking)

- values 키를 `image.tag` → `image.version` 으로 변경. 기존 `image.tag`를 넘기던 values는 더 이상 태그가 반영되지 않습니다. 옮길 때 `image.tag` → `image.version` 으로 키를 바꾸세요.

### Added

- `resources` 값 추가(기본 `{}`). 설정하지 않으면 이전과 동일하게 동작합니다.

## 0.6.0 (appVersion 1.27)

### Added

- `resources` 값 없이 동작하던 chart에 리소스 요청/제한을 넣을 자리를 준비.

## 0.5.1 (appVersion 1.27)

### Fixed

- 템플릿 렌더 오타 수정. values 인터페이스 변경 없음.
