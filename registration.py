import torch
import numpy as np
import cv2
from compute_offset import ApplyShifts
from LoadData import load_data as ld
from correlation_torch import NormXCorr2
import time

class NCCProject():

    def __init__(self, template_frame, path):
        self.LOAD=ld(1)
        cap=cv2.VideoCapture(path)
        ret, raw_frame=cap.read()
        raw_frame=cv2.cvtColor(raw_frame, cv2.COLOR_RGB2GRAY)
        raw_frame=torch.tensor(raw_frame, dtype=torch.float32)
        self.template=torch.tensor(template_frame, dtype=torch.float32).cuda()
        self.kernel=torch.tensor(self.LOAD.generate_kernel((15,15)), dtype=torch.float32)#kernel尺寸可能后期要根据神经元大小调整
        self.sum1, self.a_rot_complex, self.b_complex, self.Zeros, self.theta, self.template_buffer = self.LOAD.SetParameters(
            raw_frame, self.kernel, CROP=False, use_gpu=True)
        self.kernel=self.kernel.cuda()
        self.ith=0


    def NCC_framebyframe(self, frame):
        frame = torch.tensor(frame, dtype=torch.float32).cuda()
        preprocess_frame = self.LOAD.filter_frame(frame, self.kernel)
        normxcorr2_general_output = NormXCorr2(self.template, preprocess_frame)
        output, _ = normxcorr2_general_output.normxcorr2_general(self.sum1, self.a_rot_complex, self.b_complex,
                                                                 self.Zeros)
        Shift = ApplyShifts(output)
        new_filtered_frame, _, _ = Shift.apply_shift(preprocess_frame, self.theta)
        new_raw_frame, _ , _ = Shift.apply_shift(frame, self.theta)

        new_filtered_frame = new_filtered_frame.squeeze(0)
        self.template_buffer[:, :, self.ith] = new_filtered_frame
        self.ith+=1
        if self.ith%200==0:
            mean_temp = torch.mean(self.template_buffer, dim=2)
            self.template = (self.template + mean_temp) / 2
            self.ith=0
        new_raw_frame = new_raw_frame.squeeze(0)
        new_raw_frame=new_raw_frame.cpu().numpy()

        return bytearray(new_raw_frame.astype(np.uint8))

class Preprocess():
    def __init__(self, path):
        # print("E:\C++pythontest\mylab4.986\debug")
        self.path=path

    def get_video(self):
        print(self.path)
        cap=cv2.VideoCapture(self.path)
        nums=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video=np.empty((height, width, nums))
        i=0
        while(cap.isOpened() and i<nums):
            ret, frame=cap.read()
            frame=cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            video[:,:,i]=frame
            i+=1

        return video

    def generate_template(self):
        init_video=self.get_video()
        init_video = torch.tensor(init_video, dtype=torch.float32)
        LOAD=ld(1)
        kernel=torch.tensor(LOAD.generate_kernel((15,15)), dtype=torch.float32)
        sum1, a_rot_complex, b_complex, Zeros, theta, _ = LOAD.SetParameters(
            init_video[:,:,0], kernel, CROP=False, use_gpu=True)

        init_video = init_video.cuda()
        kernel=kernel.cuda()
        template = init_video[:, :, 0]
        preprocess_temp = LOAD.filter_frame(template, kernel)
        for i in range(200):

            frame = init_video[:, :, i]

            preprocess_frame = LOAD.filter_frame(frame, kernel)
            normxcorr2_general_output = NormXCorr2(preprocess_temp, preprocess_frame)
            output, _ = normxcorr2_general_output.normxcorr2_general(sum1, a_rot_complex, b_complex,
                                                                     Zeros)
            Shift = ApplyShifts(output)
            new_filtered_frame, _, _ = Shift.apply_shift(preprocess_frame, theta)
            new_filtered_frame = new_filtered_frame.squeeze(0)
            preprocess_temp = preprocess_temp * (i + 1) / (i + 2) + new_filtered_frame / (i + 2)

        preprocess_temp=preprocess_temp.cpu().numpy()

        return preprocess_temp

# path='D:/msCam1.avi'
# Pre=Preprocess(path)
# template=Pre.generate_template()
# cap=cv2.VideoCapture(path)
# ret,frame=cap.read()
# frame=cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
# NCCInstance=NCCProject(template, path)
# start=time.time()
# fixed_frame=NCCInstance.NCC_framebyframe(frame)
# print(time.time()-start)