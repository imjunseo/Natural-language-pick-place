"""Deterministic command parsing and transactional chess planning."""
import re
import chess

class CommandError(ValueError):
    pass

PIECES = {'폰': chess.PAWN, '나이트': chess.KNIGHT, '비숍': chess.BISHOP,
          '룩': chess.ROOK, '퀸': chess.QUEEN, '킹': chess.KING}

def parse_command(text, board):
    text = text.strip().lower()
    if any(word in text for word in ('하지', '말고', '말아', '취소', '아니', '또는', '혹은', '말라')):
        raise CommandError('부정·선택 표현이 포함되었습니다. 실행할 한 수를 명확히 지정하세요.')
    exact = re.fullmatch(r'([a-h][1-8])([a-h][1-8])([qrbn]?)', text)
    if exact:
        move = chess.Move.from_uci(text)
    else:
        squares = re.findall(r'(?<![a-z0-9])([a-h][1-8])(?![a-z0-9])', text)
        if len(squares) != 2:
            raise CommandError('출발 칸과 도착 칸을 각각 하나씩 지정하세요. 예: e2 폰을 e4로 옮겨')
        move = chess.Move.from_uci(''.join(squares))
        names = [kind for name, kind in PIECES.items() if name in text]
        source = board.piece_at(move.from_square)
        if len(set(names)) > 1 or (names and (not source or source.piece_type != names[0])):
            raise CommandError('말 이름이 출발 칸의 말과 일치하지 않습니다.')
        if ('백' in text and source and not source.color) or ('흑' in text and source and source.color):
            raise CommandError('말 색상이 출발 칸과 일치하지 않습니다.')
    if move not in board.legal_moves:
        raise CommandError('현재 차례·배치에서 불가능한 수입니다. 프로모션은 e7e8q처럼 지정하세요.')
    return move

class Session:
    def __init__(self, fen=chess.STARTING_FEN):
        self.board = chess.Board(fen)
        if not self.board.is_valid():
            raise CommandError('유효하지 않은 보드입니다.')
        self.entities = {sq: f'{"white" if p.color else "black"}_{chess.piece_name(p.piece_type)}_{chess.square_name(sq)}'
                         for sq, p in self.board.piece_map().items()}
        self.blocked = False
        self.ply = 0

    def plan(self, text):
        if self.blocked:
            raise CommandError('실행 결과 불명 또는 검증 실패 상태입니다. 장면을 재설정하고 다시 시작하세요.')
        move = parse_command(text, self.board)
        # Physical replacement of promotion pieces is deliberately not faked.
        if move.promotion:
            raise CommandError('규칙상 프로모션이지만 말 교체 동작은 아직 지원하지 않습니다.')
        transfers = []
        capture_sq = move.to_square
        if self.board.is_en_passant(move):
            capture_sq += -8 if self.board.turn else 8
        if self.board.is_capture(move):
            transfers.append({'entity': self.entities[capture_sq], 'from': chess.square_name(capture_sq),
                              'to': 'capture_bin'})
        transfers.append({'entity': self.entities[move.from_square], 'from': chess.square_name(move.from_square),
                          'to': chess.square_name(move.to_square)})
        if self.board.is_castling(move):
            rank = chess.square_rank(move.from_square)
            kingside = move.to_square > move.from_square
            src = chess.square(7 if kingside else 0, rank)
            dst = chess.square(5 if kingside else 3, rank)
            transfers.append({'entity': self.entities[src], 'from': chess.square_name(src), 'to': chess.square_name(dst)})
        after = self.board.copy()
        after.push(move)
        return {'uci': move.uci(), 'before_fen': self.board.fen(), 'after_fen': after.fen(), 'transfers': transfers}

    def commit(self, plan):
        if self.blocked or plan['before_fen'] != self.board.fen():
            raise CommandError('상태가 바뀐 이동 계획입니다.')
        mapping = dict(self.entities)
        for action in plan['transfers']:
            src = chess.parse_square(action['from'])
            entity = mapping.pop(src)
            if action['to'] != 'capture_bin':
                mapping[chess.parse_square(action['to'])] = entity
        self.board.push_uci(plan['uci'])
        self.entities = mapping
        self.ply += 1
