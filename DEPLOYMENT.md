# Streamlit Community Cloud 배포 가이드

## 📋 배포 준비사항

### 1. GitHub 레포지토리 생성
1. GitHub에서 새 레포지토리 생성
2. 프로젝트 파일들 업로드

### 2. 필요한 파일들 확인
- ✅ `app.py` (메인 애플리케이션)
- ✅ `requirements.txt` (패키지 의존성)
- ✅ `.streamlit/config.toml` (Streamlit 설정)
- ✅ `pages/` 폴더 (페이지 컴포넌트들)
- ✅ `utils/` 폴더 (유틸리티 함수들)

## 🚀 Streamlit Community Cloud 배포

### 1. Streamlit Community Cloud 접속
1. https://share.streamlit.io/ 방문
2. GitHub 계정으로 로그인

### 2. 새 앱 배포
1. "New app" 클릭
2. GitHub 레포지토리 선택
3. 브랜치: `main` (또는 `master`)
4. 메인 파일: `app.py`
5. 앱 URL 설정 (선택사항)

### 3. 환경변수 설정 ⚠️ 중요!
**Advanced settings > Secrets** 섹션에서:
```toml
ADMIN_EMAIL = "관리자이메일@example.com"
ADMIN_PASSWORD = "안전한비밀번호123"
```

### 4. 배포 시작
- "Deploy!" 버튼 클릭
- 초기 배포는 2-3분 소요

## 🔧 배포 후 설정

### 1. 관리자 계정 테스트
- 배포된 URL에서 관리자 로그인 테스트
- 환경변수가 제대로 설정되었는지 확인

### 2. 참여자 등록
1. 관리자로 로그인
2. 참여자 이메일 일괄 등록
3. 팀 생성 및 할당

### 3. 학생 테스트
- 등록된 이메일로 학생 로그인 테스트
- 투표 기능 정상 작동 확인

## 📱 모바일 최적화 확인

투표 시스템은 모바일 전용으로 설계되었으므로:
- 스마트폰에서 접속하여 UI 확인
- 터치 친화적 인터페이스 테스트
- 투표 선택 및 제출 기능 테스트

## 🔄 업데이트 방법

코드 수정 후:
1. GitHub 레포지토리에 푸시
2. Streamlit Cloud에서 자동 재배포
3. 환경변수는 Streamlit Cloud에서 직접 수정

## 🆘 문제 해결

### 환경변수 오류
- Streamlit Cloud > App settings > Secrets에서 확인
- ADMIN_EMAIL, ADMIN_PASSWORD 정확히 설정했는지 확인

### 패키지 오류
- `requirements.txt` 파일 확인
- 버전 호환성 문제시 버전 범위 조정

### 접속 오류
- GitHub 레포지토리가 public인지 확인
- 메인 파일 경로가 `app.py`인지 확인

## 📊 성능 모니터링

Streamlit Community Cloud에서 제공하는:
- 앱 사용량 통계
- 에러 로그 모니터링
- 리소스 사용량 확인

---

**배포 완료 후**: 투표 이벤트 전에 모든 기능을 충분히 테스트해보세요!