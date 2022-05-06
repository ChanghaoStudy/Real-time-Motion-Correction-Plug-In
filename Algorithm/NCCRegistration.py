import torch
import numpy as np
import time
from compute_offset import ApplyShifts
from LoadData import load_data as ld
from correlation_torch import NormXCorr2
import matplotlib.pyplot as plt

class NCCMotionCorrection():

    def __init__(self, sum1, a_rot_complex, b_complex, Zeros, theta, template_buffer, crop_size):
        self.sum1=sum1
        self.a_rot_complex=a_rot_complex
        self.b_complex=b_complex
        self.Zeros=Zeros
        self.theta=theta
        self.template_buffer=template_buffer
        self.crop_size=crop_size


    def generate_template(self, init_batch, init_video, kernel, use_gpu, CROP):

        if use_gpu==True:
            if CROP== True:
                template=init_video[:,:,0]

                filtered_temp=ld(0).filter_frame(template, kernel)
                preprocess_temp=ld(0).cut_frame(filtered_temp, self.crop_size)
                for i in range(init_batch):
                    frame=init_video[:,:,i]
                    frame=frame.cuda()
                    filtered_frame=ld(0).filter_frame(frame, kernel)
                    preprocess_frame=ld(0).cut_frame(filtered_frame, self.crop_size)
                    normxcorr2_general_output=NormXCorr2(preprocess_temp, preprocess_frame)
                    output, _=normxcorr2_general_output.normxcorr2_general(self.sum1, self.a_rot_complex, self.b_complex, self.Zeros)
                    Shift=ApplyShifts(output)
                    new_filtered_frame,_,_=Shift.apply_shift(preprocess_frame, self.theta)
                    new_filtered_frame=new_filtered_frame.squeeze(0)
                    preprocess_temp=preprocess_temp*(i+1)/(i+2)+new_filtered_frame/(i+2)
            else:
                template=init_video[:,:,0]
                template=template.cuda()
                preprocess_temp=ld(0).filter_frame(template, kernel)
                # h, w=preprocess_temp.shape
                # print(h,w)
                # buffer=torch.zeros([h,w,init_batch])
                # buffer=buffer.cuda()

                for i in range(init_batch):
                    frame=init_video[:,:,i]
                    frame=frame.cuda()
                    preprocess_frame=ld(0).filter_frame(frame, kernel)
                    normxcorr2_general_output=NormXCorr2(preprocess_temp, preprocess_frame)
                    output, _=normxcorr2_general_output.normxcorr2_general(self.sum1, self.a_rot_complex, self.b_complex, self.Zeros)
                    Shift=ApplyShifts(output)
                    new_filtered_frame,_,_=Shift.apply_shift(preprocess_frame, self.theta)
                    new_filtered_frame=new_filtered_frame.squeeze(0)

                    preprocess_temp=preprocess_temp*(i+1)/(i+2)+new_filtered_frame/(i+2)
                # preprocess_temp=torch.mean(buffer, dim=2)
        else:
            if CROP==True:
                template=init_video[:,:,0]
                filtered_temp=ld(0).filter_frame(template, kernel)
                preprocess_temp=ld(0).cut_frame(filtered_temp, self.crop_size)
                for i in range(init_batch):
                    frame=init_video[:,:,i]
                    filtered_frame=ld(0).filter_frame(frame, kernel)
                    preprocess_frame=ld(0).cut_frame(filtered_frame, self.crop_size)
                    normxcorr2_general_output=NormXCorr2(preprocess_temp, preprocess_frame)
                    output, _=normxcorr2_general_output.normxcorr2_general(self.sum1, self.a_rot_complex, self.b_complex, self.Zeros)
                    Shift=ApplyShifts(output)
                    new_filtered_frame,_,_=Shift.apply_shift(preprocess_frame, self.theta)
                    new_filtered_frame=new_filtered_frame.squeeze(0)
                    preprocess_temp=preprocess_temp*(i+1)/(i+2)+new_filtered_frame/(i+2)
            else:
                template=init_video[:,:,0]
                preprocess_temp=ld(0).filter_frame(template, kernel)
                for i in range(init_batch):
                    frame=init_video[:,:,i]
                    preprocess_frame=ld(0).filter_frame(frame, kernel)
                    normxcorr2_general_output=NormXCorr2(preprocess_temp, preprocess_frame)
                    output, _=normxcorr2_general_output.normxcorr2_general(self.sum1, self.a_rot_complex, self.b_complex, self.Zeros)
                    Shift=ApplyShifts(output)
                    new_filtered_frame,_,_=Shift.apply_shift(preprocess_frame, self.theta)
                    new_filtered_frame=new_filtered_frame.squeeze(0)
                    preprocess_temp=preprocess_temp*(i+1)/(i+2)+new_filtered_frame/(i+2)
        return preprocess_temp

    def Online_NCC_motion_correction(self, video, new_video, x_shift, y_shift, preprocess_temp, kernel, use_gpu, CROP):


        if use_gpu==True:
            if CROP==True:
                for i in range(video.shape[2]):
                    frame=video[:,:,i]
                    frame=frame.cuda()
                    filtered_frame=ld(0).filter_frame(frame, kernel)
                    preprocess_frame=ld(0).cut_frame(filtered_frame, self.crop_size)

                    normxcorr2_general_output=NormXCorr2(preprocess_temp, preprocess_frame)
                    output, _=normxcorr2_general_output.normxcorr2_general(self.sum1, self.a_rot_complex, self.b_complex, self.Zeros)
                    Shift=ApplyShifts(output)
                    new_filtered_frame,_,_=Shift.apply_shift(preprocess_frame, self.theta)
                    new_raw_frame, y_shift[:,i], x_shift[:,i]=Shift.apply_shift(frame, self.theta)
                    new_filtered_frame=new_filtered_frame.squeeze(0)
                    new_raw_frame=new_raw_frame.squeeze(0)

                    #update template
                    #The weight of each componet or the method of updating template
                    #can be modified in this part.
                    self.template_buffer[:,:,i%200]=new_filtered_frame
                    if (i+1)%200==0:
                        mean_temp=torch.mean(self.template_buffer, dim=2)
                        preprocess_temp=(preprocess_temp+mean_temp)/2
                    new_raw_frame=new_raw_frame.cpu()
                    new_video[:,:,i]=new_raw_frame
            else:
                for i in range(video.shape[2]):

                    frame=video[:,:,i]
                    frame=frame.cuda()
                    preprocess_frame=ld(0).filter_frame(frame, kernel)




                    normxcorr2_general_output=NormXCorr2(preprocess_temp, preprocess_frame)
                    output, _=normxcorr2_general_output.normxcorr2_general(self.sum1, self.a_rot_complex, self.b_complex, self.Zeros)



                    Shift=ApplyShifts(output)
                    new_filtered_frame,_,_=Shift.apply_shift(preprocess_frame, self.theta)
                    new_raw_frame, y_shift[:,i], x_shift[:,i]=Shift.apply_shift(frame, self.theta)

                    new_filtered_frame=new_filtered_frame.squeeze(0)
                    new_raw_frame=new_raw_frame.squeeze(0)


                    # update template
                    # The weight of each componet or the method of updating template
                    # can be modified in this part.
                    self.template_buffer[:,:,i%200]=new_filtered_frame
                    if (i+1)%200==0:
                        mean_temp=torch.mean(self.template_buffer, dim=2)
                        # preprocess_temp=(preprocess_temp+mean_temp)/2
                        k=(i+1)/200
                        preprocess_temp=preprocess_temp*(k+1)/(k+2)+mean_temp/(k+2)


                    new_raw_frame=new_raw_frame.cpu()
                    new_video[:,:,i]=new_raw_frame
        else:
            if CROP==True:
                for i in range(video.shape[2]):
                    frame=video[:,:,i]

                    filtered_frame=ld(0).filter_frame(frame, kernel)
                    preprocess_frame=ld(0).cut_frame(filtered_frame, self.crop_size)

                    normxcorr2_general_output=NormXCorr2(preprocess_temp, preprocess_frame)
                    output, _=normxcorr2_general_output.normxcorr2_general(self.sum1, self.a_rot_complex, self.b_complex, self.Zeros)
                    Shift=ApplyShifts(output)
                    new_filtered_frame,_,_=Shift.apply_shift(preprocess_frame, self.theta)
                    new_raw_frame, y_shift[:,i], x_shift[:,i]=Shift.apply_shift(frame, self.theta)
                    new_filtered_frame=new_filtered_frame.squeeze(0)
                    new_raw_frame=new_raw_frame.squeeze(0)

                    #update template
                    #The weight of each componet or the method of updating template
                    #can be modified in this part.
                    self.template_buffer[:,:,i%200]=new_filtered_frame
                    if (i+1)%200==0:
                        mean_temp=torch.mean(self.template_buffer, dim=2)
                        preprocess_temp=(preprocess_temp+mean_temp)/2

                    new_video[:,:,i]=new_raw_frame
            else:
                for i in range(video.shape[2]):
                    filter_start_time = time.time()
                    frame=video[:,:,i]
                    preprocess_frame=ld(0).filter_frame(frame, kernel)
                    filter_time += time.time() - filter_start_time

                    NCC_start_time = time.time()
                    normxcorr2_general_output=NormXCorr2(preprocess_temp, preprocess_frame)
                    output, _=normxcorr2_general_output.normxcorr2_general(self.sum1, self.a_rot_complex, self.b_complex, self.Zeros)
                    NCC_time += time.time() - NCC_start_time

                    shift_start_time = time.time()
                    Shift=ApplyShifts(output)
                    new_filtered_frame,_,_=Shift.apply_shift(preprocess_frame, self.theta)
                    new_raw_frame, y_shift[:,i], x_shift[:,i]=Shift.apply_shift(frame, self.theta)

                    new_filtered_frame=new_filtered_frame.squeeze(0)
                    new_raw_frame=new_raw_frame.squeeze(0)
                    shift_time += time.time() - shift_start_time

                    #update template
                    #The weight of each componet or the method of updating template
                    #can be modified in this part.
                    self.template_buffer[:,:,i%200]=new_filtered_frame
                    if (i+1)%200==0:
                        mean_temp=torch.mean(self.template_buffer, dim=2)
                        preprocess_temp=(preprocess_temp+mean_temp)/2

                    new_video[:,:,i]=new_raw_frame

        return new_video, x_shift, y_shift










