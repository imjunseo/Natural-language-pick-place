import unittest
from unittest.mock import patch
import subprocess
import chess
from chess_robot.core import Session, CommandError
from chess_robot.backends import MemoryBackend, GazeboPoseBackend
from chess_robot.vision import render_reference,detect_occupancy,expected_occupancy

class FlowTests(unittest.TestCase):
    def apply(self,s,text):
        plan=s.plan(text); s.commit(plan); return plan
    def test_korean_and_capture_entity_identity(self):
        s=Session()
        self.apply(s,'e2 폰을 e4로 옮겨'); self.apply(s,'d7d5')
        p=self.apply(s,'e4d5')
        self.assertEqual(p['transfers'][0]['to'],'capture_bin')
        self.assertEqual(s.entities[chess.D5],'white_pawn_e2')
        self.assertEqual(len(s.entities),31)
    def test_reject_without_mutation(self):
        for text in ['e2e5','e7e5','폰 앞으로','e2 룩을 e4로','e2 e4 e5','흑 폰 e2 e4','e2에서 e4로 옮기지 말고','e2 e4 취소']:
            s=Session(); before=s.board.fen()
            with self.assertRaises(CommandError): s.plan(text)
            self.assertEqual(s.board.fen(),before)
    def test_castle(self):
        s=Session('r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1')
        p=self.apply(s,'e1g1')
        self.assertEqual(len(p['transfers']),2)
        self.assertEqual(s.entities[chess.F1],'white_rook_h1')
    def test_en_passant(self):
        s=Session()
        for cmd in ['e2e4','a7a6','e4e5','d7d5']: self.apply(s,cmd)
        p=self.apply(s,'e5d6')
        self.assertEqual(p['transfers'][0]['from'],'d5')
        self.assertNotIn(chess.D5,s.entities)
    def test_promotion_rejected_before_execution(self):
        s=Session('7k/P7/8/8/8/8/8/7K w - - 0 1')
        with self.assertRaises(CommandError): s.plan('a7a8q')
    def test_failed_verification_blocks(self):
        s=Session(); p=s.plan('e2e4'); s.blocked=True
        with self.assertRaises(CommandError): s.commit(p)
        with self.assertRaises(CommandError): s.plan('e2e4')
        self.assertEqual(s.board.fen(),chess.STARTING_FEN)
    def test_reference_image_after_capture(self):
        s=Session(); b=MemoryBackend(s.board)
        for cmd in ['e2e4','d7d5','e4d5']:
            p=s.plan(cmd); b.execute(p)
            self.assertTrue(b.verify(p)); s.commit(p)
            self.assertEqual(detect_occupancy(render_reference(b.board)),expected_occupancy(s.board))
    @patch('chess_robot.backends.subprocess.run')
    def test_pose_false_response_is_failure(self,run):
        run.return_value=subprocess.CompletedProcess([],0,'data: false','')
        b=GazeboPoseBackend(chess.Board())
        with self.assertRaises(RuntimeError): b.set_pose('white_pawn_e2',(0,0,0))
    def test_stale_plan(self):
        s=Session(); p=s.plan('e2e4'); self.apply(s,'d2d4')
        with self.assertRaises(CommandError): s.commit(p)

if __name__=='__main__': unittest.main()
