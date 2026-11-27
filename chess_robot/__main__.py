import argparse
import json
from pathlib import Path
import chess
from .core import Session, CommandError
from .backends import MemoryBackend, GazeboPoseBackend

def main():
    parser=argparse.ArgumentParser(description='개인 체스 로봇 개발 버전; 아직 OMX-AI 팔 제어 미구현')
    parser.add_argument('--backend',choices=['memory','gazebo-pose'],default='memory')
    parser.add_argument('--command',action='append',help='여러 번 지정하면 순서대로 실행')
    parser.add_argument('--log',default='runs/session.jsonl')
    parser.add_argument('--reference-images',action='store_true',help='합성 이미지 비전 회귀 검증 (실카메라 아님)')
    args=parser.parse_args()
    if args.backend=='gazebo-pose' and args.reference_images:
        parser.error('Gazebo 실장면 검증에 합성 이미지를 사용할 수 없습니다.')
    s=Session()
    backend=MemoryBackend(s.board) if args.backend=='memory' else GazeboPoseBackend(s.board)
    log=Path(args.log); log.parent.mkdir(parents=True,exist_ok=True)
    print('실행 모드:',backend.label)
    if args.backend=='gazebo-pose':
        print('새 초기 배치 Gazebo 장면에서 시작하세요. 포즈 변경만 수행하며, 이동 후 수동 확인 전에는 다음 명령을 실행하지 않습니다.')
    def run(text):
        record={'command':text,'backend':backend.label}
        try:
            plan=s.plan(text)
            record['plan']=plan
            backend.execute(plan)
            verified=backend.verify(plan)
            if args.reference_images:
                import cv2
                from .vision import render_reference,detect_occupancy,expected_occupancy
                b=chess.Board(plan['after_fen'])
                image=render_reference(backend.board)
                cv2.imwrite(str(log.parent/f'after_{s.ply+1}.png'),image)
                verified=verified and detect_occupancy(image)==expected_occupancy(b)
                record['verification']='synthetic-image-regression'
            if args.backend=='gazebo-pose':
                verified=input('장면에서 이동·잡힌 말 위치를 확인했나요? 맞으면 yes: ').strip()=='yes'
                record['verification']='human-confirmed' if verified else 'unconfirmed'
            if not verified:
                s.blocked=True
                record['status']='blocked'
                print('미확인: 논리 보드를 갱신하지 않고 정지합니다. 장면 재설정 필요.')
            else:
                s.commit(plan)
                record['status']='committed'
                print(plan['uci'], '완료 / 다음 차례:', '백' if s.board.turn else '흑')
        except CommandError as e:
            record.update(status='rejected',reason=str(e)); print('거절:',e)
        except Exception as e:
            s.blocked=True
            record.update(status='blocked',reason=str(e)); print('실행 중단:',e)
        record['fen']=s.board.fen()
        with log.open('a',encoding='utf-8') as f: f.write(json.dumps(record,ensure_ascii=False)+'\n')
        return record['status']
    if args.command:
        statuses=[]
        for command in args.command:
            statuses.append(run(command))
            if s.blocked: break
        return 0 if all(v=='committed' for v in statuses) else 1
    while not s.blocked:
        try: command=input('이동 명령 (quit 종료): ')
        except (EOFError,KeyboardInterrupt): break
        if command.strip().lower()=='quit': break
        run(command)
    return 1 if s.blocked else 0

if __name__=='__main__':
    raise SystemExit(main())
