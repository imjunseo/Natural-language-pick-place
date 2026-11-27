"""Memory reference and Gazebo pose-only test backend. Neither controls an arm."""
import json
import re
import subprocess
import time
from pathlib import Path
import chess

ROOT = Path(__file__).resolve().parents[1]
COORDS = json.loads((ROOT / 'sim/square_centers.json').read_text())

class MemoryBackend:
    label = 'memory-reference'
    def __init__(self, board):
        self.board = board.copy()
    def execute(self, plan):
        self.board.push_uci(plan['uci'])
    def verify(self, plan):
        return self.board.fen() == plan['after_fen']

class GazeboPoseBackend:
    label = 'gazebo-pose-test-NO-ARM'
    def __init__(self, board):
        if board.fen() != chess.STARTING_FEN:
            raise ValueError('Gazebo 경로는 새로 시작한 초기 배치 장면만 지원합니다.')
        self.captured = 0
    def set_pose(self, name, xyz):
        req = f'name: "{name}", position: {{x: {xyz[0]}, y: {xyz[1]}, z: {xyz[2]}}}, orientation: {{w: 1}}'
        result = subprocess.run(['gz','service','-s','/world/chess_world/set_pose',
            '--reqtype','gz.msgs.Pose','--reptype','gz.msgs.Boolean','--timeout','5000','--req',req],
            capture_output=True, text=True, timeout=8)
        if result.returncode or not re.search(r'data:\s*true\b', result.stdout):
            raise RuntimeError('Gazebo 위치 변경 응답 실패: ' + result.stdout + result.stderr)
    def execute(self, plan):
        # Service responses acknowledge commands, not grasp or physical completion.
        for action in plan['transfers']:
            a = COORDS['squares'][action['from']]
            start = (a['x'], a['y'], a['z'])
            if action['to'] == 'capture_bin':
                end = (0.10 + (self.captured % 8)*0.03, 0.22 + (self.captured//8)*0.03, 0.005)
                self.captured += 1
            else:
                b = COORDS['squares'][action['to']]
                end = (b['x'], b['y'], b['z'])
            # Pose animation for integration testing only: no inverse kinematics/contact.
            waypoints = [start, (start[0],start[1],0.10), (end[0],end[1],0.10),end]
            for left,right in zip(waypoints,waypoints[1:]):
                for step in range(1,7):
                    t=step/6
                    self.set_pose(action['entity'], tuple(x+(y-x)*t for x,y in zip(left,right)))
                    time.sleep(0.04)
    def verify(self, plan):
        # Never pretend a service acknowledgement is camera verification.
        return False
