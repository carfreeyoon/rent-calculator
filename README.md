# 카프리오 견적 비교 계산기

할부·렌트·리스 조건을 비교하고 고객용 링크를 만드는 Streamlit 앱. 견적 제안서(`carfreeyoon/carfreeoh-proposal`) 및 CRM과 별도 서비스다.

## 현행 코드

- GitHub: `carfreeyoon/rent-calculator`, 기본 브랜치 `main`.
- `app.py`: 영업자 입력, 계산, 고객 화면, 공유 링크. 현재 계산식과 UI가 한 파일에 함께 있다.
- `share_backend.py`, `share_store.py`: 공유 링크 저장·조회와 저장소 전환. `requirements.txt`: 실행 의존성.
- 고객 링크: `https://compare-carfreeoh.com/?view=client&q=<공유값>`. `q`가 있어야 고객 화면으로 분기한다. 영업자 화면은 `APP_PASSWORD`를 요구한다.
- `landing/index.html`은 도메인 리디렉션 파일이지만 현재 운영 도메인의 응답과 목적지가 다르다.

## 2026-11-25 인계 현황

| 구분 | 확인한 내용 |
| --- | --- |
| 운영 진입 | `compare-carfreeoh.com` → `carfreeoh-rentcalculator.streamlit.app` |
| 테스트 진입 | `compare-carfreeoh.com/test` → `test-carfreeoh.streamlit.app`. 정근님이 프론트 테스트 배포 주소로 확인 |
| 저장소의 landing 파일 | `rent-calculator.streamlit.app`으로 리디렉션. 현재 도메인 응답과 불일치 |
| GitHub main | 확인 시점 `2e50fb97` (11/03). `work-prepayment`은 main보다 이전 상태 |
| 미확인 | 테스트·운영 Streamlit 앱의 실제 GitHub 저장소·브랜치·실행 커밋, 현재 도메인 배포 원본 |

주소의 리디렉션만으로 Streamlit 실행 코드가 이 저장소의 `main`과 같다고 판단하지 않는다.

## 공유 링크 주의사항

- 코드의 기본 설정은 `SHARE_BACKEND=supabase`, `SHARE_WRITES_PAUSED=true`다. 실제 Streamlit 비밀 설정값과 Neon 전환 완료 여부는 아직 확인 전이다.
- 짧은 링크 저장이 중단·실패하면 공유 데이터를 URL에 담은 긴 링크를 발급한다.
- 저장소를 바꾸기 전에 이전 짧은 링크의 조회, 기존 자료 이관, 새 링크 발급을 각각 확인해야 한다.
- 저장소는 현재 공개다. 비밀번호·DB 주소 등 비밀값을 코드나 이 문서에 적지 않는다.

## 다음 작업 순서

1. `test-carfreeoh.streamlit.app`의 연결 저장소·브랜치·실행 커밋을 확인한다. 운영 앱과 도메인의 배포 원본도 따로 확인한다.
2. Claude가 테스트 화면의 UI를 보완한다. 계산식, 금액, 공유 데이터 형식의 변경은 UI와 분리해 검토한다.
3. 테스트 앱에서 할부·렌트·리스 결과, 기존/새 고객 링크, 모바일·PC를 검증한다.
4. 정근님 화면 확인 뒤 동일 검증 커밋을 운영에 반영하고 링크 라우팅을 확인한다. 배포일·커밋·복구 지점을 이 문서에 적는다.

사람이 정하는 UI 기준은 [사이트·견적 서비스 노션](https://app.notion.com/p/40bfb794a56181128436dd5aa5fa5be3) 아래에 둔다. 코드·배포 기준은 여기서 관리한다.
