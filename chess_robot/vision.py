"""Synthetic color occupancy baseline, not real chess-piece classification."""
import cv2
import numpy as np
import chess

def render_reference(board):
    image = np.zeros((640,640,3), np.uint8)
    for sq in chess.SQUARES:
        file,rank = chess.square_file(sq),chess.square_rank(sq)
        x,y=file*80,(7-rank)*80
        image[y:y+80,x:x+80] = (180,180,180) if (file+rank)%2 else (75,75,75)
        p=board.piece_at(sq)
        if p:
            # Saturated markers intentionally decouple occupancy from piece identity.
            cv2.circle(image,(x+40,y+40),23,(255,80,20) if p.color else (20,70,255),-1)
    return image

def detect_occupancy(image, corners=None):
    if image is None:
        raise ValueError('이미지를 읽지 못했습니다.')
    if corners is not None:
        points=np.asarray(corners,dtype=np.float32)
        if points.shape != (4,2) or abs(cv2.contourArea(points)) < 100:
            raise ValueError('네 모서리는 a8,h8,h1,a1 순서로 지정하세요.')
        target=np.float32([[0,0],[639,0],[639,639],[0,639]])
        image=cv2.warpPerspective(image,cv2.getPerspectiveTransform(points,target),(640,640))
    if image.shape[:2] != (640,640):
        raise ValueError('모서리 보정 없이 사용할 때는 640x640 정면 보드 이미지가 필요합니다.')
    hsv=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    result={}
    for sq in chess.SQUARES:
        x,y=chess.square_file(sq)*80,(7-chess.square_rank(sq))*80
        patch=hsv[y+20:y+60,x+20:x+60]
        blue=np.mean((patch[:,:,0]>90)&(patch[:,:,0]<130)&(patch[:,:,1]>120))
        red=np.mean(((patch[:,:,0]<15)|(patch[:,:,0]>170))&(patch[:,:,1]>120))
        result[chess.square_name(sq)]='white' if blue>0.25 else 'black' if red>0.25 else 'empty'
    return result

def expected_occupancy(board):
    return {chess.square_name(sq): ('white' if board.color_at(sq) else 'black')
            if board.piece_at(sq) else 'empty' for sq in chess.SQUARES}
