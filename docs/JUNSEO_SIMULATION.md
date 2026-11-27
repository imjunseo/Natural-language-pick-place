# 준서 개인 시뮬레이션 버전

팀원별로 전체 시스템을 독립 개발한 후 결과를 비교한다. 이 브랜치는 준서 버전이다. 역할 분담 방식으로 개발하지 않는다.

## 현재 구현 수준

| 기능 | 상태 | 검증 |
| --- | --- | --- |
| 한국어 좌표 명령/UCI 입력 | 구현. 출발·도착 칸 필수, 지정된 말 이름·색상 불일치 거절 | Python 테스트 |
| 체스 합법 수·차례 | chess 1.11.2 사용 | 정상 수·잘못된 수·차례 테스트 |
| 일반 이동·잡기·캐슬링·앙파상 | 개체 ID를 유지하는 이동 계획 생성 | Python 테스트 |
| 프로모션 | 규칙 해석 가능, 물리 말 교체 미지원으로 실행 거절 | 거절 테스트 |
| 상태 관리 | 실행 후 검증을 통과해야 논리 보드 확정. 실패/불명 시 추가 이동 차단 | 테스트 |
| 비전 기준 예제 | 합성 컬러 마커 이미지의 칸별 점유/색상. 실제 체스 말 종류 인식 아님 | 합성 이미지 테스트 |
| Gazebo 체스판·32말·가상 카메라 | 기존 ZIP 재사용, 정적 모델과 센서 구성 | XML 파싱만 확인 |
| Gazebo 위치 이동 | set_pose 호출, 올림→수평 이동→내림. 수동 확인 필요 | 거짓 응답 처리 테스트. 실제 Gazebo 미실행 |
| OMX-AI 팔·그리퍼/역기구학/충돌·접촉/실카메라 | 아직 미구현 | 미검증 |

**전체 로봇 시뮬레이션이 완성된 상태가 아니다.** 현재 Gazebo 포즈 경로는 로봇 없이 통합 흐름을 확인하는 도구다. 말 모델을 정적으로 바꾸었으므로 물리 파지나 안정성을 평가할 수 없다. 가상 카메라 출력과 비전 기준 예제도 아직 연결되지 않았다.

## 1. 내려받기

기존 저장소가 있다면 해당 폴더에서 실행한다. 먼저 개인 수정 사항을 커밋하거나 보관한다.

```bash
git status
git fetch origin
git switch junseo-simulation
```

처음이라면:

```bash
git clone --branch junseo-simulation https://github.com/imjunseo/Natural-language-pick-place.git
cd Natural-language-pick-place
```

## 2. Python 기본 실행 — Gazebo 불필요

기존 팀 가이드의 Ubuntu 24.04 / ROS Jazzy / 시스템 OpenCV 환경을 사용한다.

```bash
source /opt/ros/jazzy/setup.bash
source ~/chess_robot_venv/bin/activate
python -m pip install -r requirements.txt
python -m chess_robot --reference-images --command 'e2 폰을 e4로 옮겨' --command d7d5 --command e4d5
```

이것은 메모리 기준 실행 및 합성 이미지 회귀 검증이다. 실제 카메라나 Gazebo를 사용하지 않는다. runs/session.jsonl에 실행 모드·이동 계획·검증 결과·FEN이 기록되고 runs/after_*.png에 합성 보드 이미지가 생성된다. 새 실행은 초기 배치에서 시작하며 기존 로그에 이어서 기록한다. 중단된 세션 복원 기능은 없다.

대화형:

```bash
python -m chess_robot
```

입력 예: e2 폰을 e4로 옮겨, e7e5, g1 나이트를 f3으로 이동. quit으로 종료한다. 음성 인식/LLM은 사용하지 않는다. 대상이 모호한 명령은 실행하지 않는다.

## 3. Gazebo 체스 장면

터미널 1, 저장소 루트에서:

```bash
source /opt/ros/jazzy/setup.bash
bash sim/start.sh
```

체스판과 32개 말이 표시되고 시뮬레이션이 재생 중인지 확인한다. 말은 종류별 높이가 다른 단순 원통이며 정교한 체스 메시가 아니다.

터미널 2, 같은 저장소 루트에서:

```bash
source /opt/ros/jazzy/setup.bash
source ~/chess_robot_venv/bin/activate
gz service -l | grep '/world/chess_world/set_pose'
python -m chess_robot --backend gazebo-pose
```

명령: e2 폰을 e4로 옮겨. Gazebo에서 말의 위치를 확인한 뒤 터미널에 yes를 입력한다. 그 후 e7e5 등 다음 수를 입력한다. 확인하지 않거나 서비스가 실패하면 정지한다. 서비스 true 응답은 카메라 검증이 아니다.

**Gazebo를 초기 배치로 새로 시작한 뒤 Python 프로그램을 시작해야 한다.** 이미 말을 움직인 장면에서 프로그램만 재시작하지 않는다. 실패 후에는 Gazebo와 프로그램 모두 다시 시작한다. 불명 상태에서 자동 재시도하지 않는다.

가상 카메라 토픽 설정값은 /chess/camera이다. 다음 명령으로 실제 생성 여부를 확인한다.

```bash
gz topic -l | grep chess
```

장면 표시, 센서 토픽, set_pose 실제 실행은 사용자 Ubuntu에서 추가 검증해야 한다. 이 코드가 작성된 작업 환경에는 ROS/Gazebo가 설치되어 있지 않았다.

## 4. 테스트

```bash
python -m unittest discover -s tests -v
```

Python 테스트 9개 통과: 한국어 이동/잡기 개체 추적, 불법·모호한 명령 거절, 캐슬링, 앙파상, 프로모션 실행 거절, 실패 시 상태 차단, 합성 이미지 점유 검증, Gazebo false 응답 처리, 오래된 계획 거절. 실행 환경은 Python 3.12.14, chess 1.11.2와 pip OpenCV headless였다. 사용자 Python 3.12 / 시스템 OpenCV 4.6 환경에서도 위 명령으로 확인한다. Gazebo 테스트는 서비스 거짓 응답에 대한 모의 테스트이며 GUI 통과를 의미하지 않는다.

## 5. 다음 구현 순서

1. 사용자 PC에서 기본 Python 실행과 체스 장면 표시 확인.
2. 가상 카메라 실제 이미지 수신, 네 모서리 보정, 이미지 기반 점유 검증. 시뮬레이터 내부 정답 상태와 이미지 인식 성능을 구분해 평가.
3. 정확한 OMX-AI 모델/공식 제어 패키지와 Jazzy 호환 구성 확정. 일반 OpenMANIPULATOR-X를 OMX-AI와 같은 모델이라고 가정하지 않음.
4. Gazebo pose 테스트 백엔드를 팔·그리퍼 제어 백엔드로 교체. 현재 좌표 파일의 프레임·단위(m)를 맞추고 개별 칸 도달 가능성 검증.
5. 정적 말 모델을 동적 모델로 전환하고 파지·마찰·충돌·놓기 확인. 단순 위치 이동 성공을 파지 성공으로 계산하지 않음.
6. 반복 시나리오 실행 및 실장비 전환. 실제 장비는 좌표/속도/파지 조건뿐 아니라 제어 연결 차이도 확인.

## 6. 독립 결과물 비교 기준

같은 초기 배치와 같은 명령 목록으로 비교한다. 예: e2e4, d7d5, e4d5, g8f6. 별도 초기화 후 e2e5 거절과 '폰 앞으로' 재질문도 확인한다.

| 항목 | 기록 |
| --- | --- |
| 자연어 | 정답/거절/재질문 결과, 지원 범위 |
| 비전 | 칸 점유·색상 정확도, 미인식률. 내부 정답값 사용 여부 |
| 이동 | 직접 포즈 변경인지 팔 파지인지, 목표 위치 오차·성공 횟수 |
| 안정성 | 실패 시 상태 유지·정지·복구 |
| 재현성 | 설치 명령·실행 명령·로그·동영상 |

## 코드 위치

- chess_robot/core.py: 명령·규칙·작업 계획·상태 관리
- chess_robot/vision.py: 합성 이미지 점유 인식 기준 예제
- chess_robot/backends.py: 메모리 기준 실행/Gazebo 포즈 테스트
- chess_robot/__main__.py: 입력·실행·검증·기록
- sim/: 기존 체스 ZIP 기반 장면·모델·좌표

참고: [Gazebo Sim 8 UserCommands](https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1UserCommands.html)의 set_pose(gz.msgs.Pose → gz.msgs.Boolean) 인터페이스를 사용한다.
