# 자연어·비전 기반 체스 로봇 — 준서 개인 시뮬레이션

OMX-AI 로봇팔과 FHD USB 웹캠을 이용한 체스 말 조작 프로젝트. 각 팀원이 전체 시스템을 독립 개발하고 결과를 비교한다. 이 junseo-simulation 브랜치는 준서의 개인 개발 버전이다.

**[개인 버전 실행 가이드·구현 상태](docs/JUNSEO_SIMULATION.md)** · [공통 환경 설정](docs/TEAM_ENVIRONMENT.md)

현재 구현: 좌표를 명시한 한국어/UCI 명령 → 체스 규칙 검사 → 이동·잡기·캐슬링·앙파상 작업 계획 → 실행 결과 검증 → 보드 상태 갱신 및 로그. 합성 이미지 점유 인식 예제와 기존 ZIP 기반 Gazebo 체스 장면을 포함한다.

```bash
source /opt/ros/jazzy/setup.bash
source ~/chess_robot_venv/bin/activate
python -m pip install -r requirements.txt
python -m chess_robot --reference-images --command 'e2 폰을 e4로 옮겨' --command d7d5 --command e4d5
```

이 명령은 메모리·합성 이미지 예제다. Gazebo는 별도 터미널에서 bash sim/start.sh로 시작하고 python -m chess_robot --backend gazebo-pose로 위치 이동 통합 테스트를 할 수 있다.

**아직 OMX-AI 팔 파지 시뮬레이션은 구현되지 않았다.** Gazebo 경로는 정적 말의 직접 포즈 변경이며 실제 팔 동작이 아니다. 가상 카메라 영상 연결·실제 말 인식·역기구학·접촉/충돌·실장비는 다음 구현 대상이다. Gazebo 런타임은 사용자 환경에서 확인이 필요하다.

Python 기능 테스트: python -m unittest discover -s tests -v (9개 통과).

팀명: 일론머스크의 왼팔 / 3분반 2조 / 과제 연계: KETI 지능로보틱스연구센터.
