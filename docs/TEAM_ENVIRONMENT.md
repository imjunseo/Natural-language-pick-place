# 팀 공통 개발 환경 설정 — 체스 로봇팔

기준일: 2026-11-26. OMX-AI 로봇팔과 FHD USB 웹캠으로 자연어·비전 기반 체스 말 조작 및 체스 규칙 검증을 구현한다. 현재는 하드웨어 없이 기본 개발 환경을 맞추는 단계다.

## 1. 팀 기준 환경

아래 확인값은 팀원 준서의 터미널 출력으로 확인했다. 신규 PC에서 전체 설치 절차를 재현한 결과는 아니다.

| 구성 | 팀 기준 | 확인 상태 |
| --- | --- | --- |
| 운영체제 | Ubuntu 24.04 LTS (확인값 24.04.5) | 확인 |
| Windows 사용 시 | WSL 2 + Ubuntu 24.04 | 팀 권장 구성. WSL 버전은 별도 확인 |
| ROS 2 | Jazzy | 환경 변수 및 Python import 확인 |
| Gazebo | Harmonic / Gazebo Sim 8.x (확인값 8.15.0) | 버전 명령 확인. GUI·물리 동작은 별도 검증 |
| ROS–Gazebo 연동 | ros-jazzy-ros-gz | 패키지 목록 확인. 통신 실험은 별도 검증 |
| Python | Ubuntu 기본 Python 3.12 계열 | 개인별 패치 버전 기록 필요 |
| OpenCV | Ubuntu python3-opencv (확인값 4.6.0) | cv2 import 확인 |
| 체스 규칙 | chess==1.11.2 | import 확인 |
| 가상환경 | ~/chess_robot_venv | 시스템 패키지 접근을 허용해 생성 |
| OMX-AI 모델·제어 | 추후 확정 | 현재 ROS 패키지 목록에서 미발견. 소스 유무 미확인 |
| 실제 로봇팔·웹캠 | 장비 확보 후 연결 | 미검증 |

Ubuntu·ROS 배포판과 Gazebo 메이저 버전을 통일한다. apt 업데이트 시 패치 버전은 달라질 수 있으므로 이 가이드는 모든 시스템 패키지를 정확히 고정하는 잠금 파일이 아니다. Gazebo 8.15.0을 맞추려고 임의 다운그레이드하지 않는다.

## 2. Windows에서 시작하는 팀원

관리자 PowerShell에서 실행한다. 이미 Ubuntu 24.04가 있으면 재설치하지 않는다.

```powershell
wsl --list --verbose
wsl --install -d Ubuntu-24.04
```

설치 과정에서 재부팅을 요구하면 재부팅하고 Ubuntu 초기 사용자 설정을 마친다. 이후 명령은 PowerShell이 아닌 Ubuntu 터미널에서 실행한다. 네이티브 Ubuntu 24.04 사용자는 이 단계를 건너뛴다.

## 3. ROS 2 Jazzy 설치

먼저 OS를 확인한다.

```bash
lsb_release -d
uname -m
```

ROS가 없는 PC는 [ROS 2 Jazzy 공식 Ubuntu 설치 안내](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)의 locale, Ubuntu Universe, ROS apt 저장소 설정 및 시스템 업데이트 단계를 먼저 완료한다. 저장소 등록 전에 아래 apt 명령을 실행하면 패키지를 찾지 못할 수 있다.

ROS 저장소 준비 후 설치한다.

```bash
sudo apt update
sudo apt install ros-jazzy-desktop ros-dev-tools
source /opt/ros/jazzy/setup.bash
```

이미 ROS Jazzy가 설치되어 있다면 재설치할 필요 없이 source 명령부터 진행한다. 다른 ROS 배포판 환경을 함께 source하지 않는다.

## 4. Gazebo·OpenCV·Python 도구

```bash
sudo apt update
sudo apt install ros-jazzy-ros-gz python3-opencv python3-venv python3-pip git
```

ROS Jazzy에는 Gazebo Harmonic 조합을 사용한다. ROS 저장소의 ros-jazzy-ros-gz가 대응 Gazebo 패키지를 설치한다. Gazebo Classic용 gazebo 명령이나 별도 OSRF 저장소 설치를 추가할 필요는 없다.

공식 기준: [Gazebo와 ROS 설치 조합](https://gazebosim.org/docs/harmonic/ros_installation/).

## 5. 가상환경 생성

새 가상환경을 만드는 팀원은 Ubuntu 기본 Python으로 생성한다. 시스템의 ROS·OpenCV를 사용하기 위해 --system-site-packages가 필요하다.

```bash
source /opt/ros/jazzy/setup.bash
/usr/bin/python3 -m venv --system-site-packages ~/chess_robot_venv
source ~/chess_robot_venv/bin/activate
python -m pip install chess==1.11.2
```

이미 가상환경에서 cv2·chess·rclpy import가 모두 성공한다면 그대로 사용한다. 기존 환경에서 cv2가 안 보이면 먼저 다음을 확인한다.

```bash
cat ~/chess_robot_venv/pyvenv.cfg
```

include-system-site-packages = false라면 기존 폴더를 삭제하지 말고 별도 환경을 만들어 비교한다.

```bash
/usr/bin/python3 -m venv --system-site-packages ~/chess_robot_venv_team
source ~/chess_robot_venv_team/bin/activate
python -m pip install chess==1.11.2
```

이 경우 이후 활성화 명령도 chess_robot_venv_team 경로를 사용한다. pip로 rclpy를 설치하지 않는다. pip의 opencv-python을 중복 설치하지 않고 apt의 python3-opencv를 사용한다. python-chess 패키지 표시가 없어도 chess import가 성공하면 현재 규칙 검사에 필요한 모듈은 준비된 것이다.

## 6. 매번 새 터미널에서

```bash
source /opt/ros/jazzy/setup.bash
source ~/chess_robot_venv/bin/activate
```

처음에는 위 명령을 직접 실행해 확인한다. 팀원이 다른 경로의 환경을 만들었다면 두 번째 경로를 맞춘다.

## 7. 공통 검증 및 결과 공유

```bash
lsb_release -d
python --version
printenv ROS_DISTRO
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import chess; print('chess:', chess.__version__); b=chess.Board(); print('e2e4 legal:', chess.Move.from_uci('e2e4') in b.legal_moves)"
python -c "import rclpy; print('ROS Python 연결 OK')"
gz sim --versions
ros2 pkg list | grep -E '^ros_gz'
```

기대 결과: Ubuntu 24.04, Python 3.12 계열, jazzy, OpenCV 4.6.0, chess 1.11.2, e2e4 legal: True, ROS Python 연결 OK, Gazebo 8.x, ros_gz 계열 패키지 목록.

준서 PC에서 확인된 패키지: ros_gz, ros_gz_bridge, ros_gz_image, ros_gz_interfaces, ros_gz_sim, ros_gz_sim_demos.

GUI 실행은 별도로 확인한다.

```bash
gz sim shapes.sdf
```

창에 기본 도형이 표시되는지 확인하고 재생 버튼으로 시뮬레이션이 진행되는지 확인한다. 이 검사는 OMX-AI 로봇 동작 검증을 포함하지 않는다. WSL에서 창이 안 뜨거나 빈 화면이면 오류 로그와 아래 출력을 함께 공유한다.

```bash
printenv DISPLAY
printenv WAYLAND_DISPLAY
gz sim -v 4 shapes.sdf
```

각 팀원은 OS, Python/OpenCV/chess/Gazebo 버전, import 결과, GUI 표시·재생 결과를 팀에 공유한다. apt 세부 버전 비교가 필요하면 다음도 공유한다.

```bash
dpkg-query -W python3-opencv ros-jazzy-ros-gz ros-jazzy-desktop
```

## 8. 저장소 내려받기

처음 한 번:

```bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/imjunseo/Natural-language-pick-place.git
cd Natural-language-pick-place
```

이미 내려받은 경우 해당 폴더에서 변경 사항을 확인한 뒤 업데이트한다.

```bash
git status
git pull --ff-only
```

가상환경 폴더, 비밀키, 개인 .env 파일은 GitHub에 올리지 않는다.

## 9. 현재 완료 범위와 다음 단계

- [x] 준서 PC의 ROS·OpenCV·chess import 확인
- [x] 준서 PC의 Gazebo 버전·ros_gz 설치 확인
- [ ] 모든 팀원의 기본 환경 및 Gazebo GUI 검증
- [ ] OMX-AI의 정확한 모델·공식 소스·Jazzy 호환 브랜치 확정
- [ ] OMX-AI 모델과 체스판·체스 말을 Gazebo에 배치
- [ ] ROS 명령을 통한 가상 로봇팔·그리퍼 동작 검증
- [ ] 저장 이미지 또는 가상 카메라를 이용한 비전 검증
- [ ] 자연어 명령 → 합법 수 검사 → 동작 계획 연결
- [ ] 장비 확보 후 실제 로봇팔·FHD USB 웹캠 연결 및 좌표 보정

현재 저장소에는 실행 가능한 로봇 시뮬레이션 코드가 아직 없다. 기본 환경 설치 완료와 전체 프로젝트 실행 완료를 구분한다. YOLO·MoveIt 2·자연어 모델/API 의존성은 구현 방식과 로봇 호환성을 정한 후 팀 공통으로 추가한다.

## 10. 자주 보이는 출력

- No LSB modules are available.: 배포판 정보가 정상 출력되면 이 메시지만으로 설치 실패가 아니다.
- rg not found: 이 가이드는 grep을 사용하므로 ripgrep 추가 설치가 필요 없다.
- rg 실패 직후 BrokenPipeError: 출력받을 프로세스가 종료되어 생긴 오류일 수 있다. grep으로 다시 실행해 확인한다.
- pip show opencv-python에서 미발견: apt 설치 OpenCV는 표시되지 않을 수 있다. import cv2로 확인한다.
- open_manipulator/omx 패키지 미발견: 현재 source된 ROS 환경에서 안 보인다는 뜻이다. 로컬 소스가 없는 것으로 단정하지 않는다.
