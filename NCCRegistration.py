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
                template=template.cuda()
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
                    frame=video[:,:,i]

                    preprocess_frame=ld(0).filter_frame(frame, kernel)

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
        return new_video, x_shift, y_shift


    def resultEvaluation(self, raw_video, fixed_video, max_x_shift, max_y_shift):
        kernel=ld(0).generate_kernel((7,7))
        raw_video=ld(0).filter(raw_video, kernel)
        fixed_video=ld(0).filter(fixed_video, kernel)

        height1=raw_video.shape[0]
        width1=raw_video.shape[1]
        fnum1=raw_video.shape[2]
        CC_raw=np.empty([1, fnum1])

        #The template can be also generated by a portion of the fixed frames
        #if the users can find part of the frames with less fluorescence fluctuation.
        template_raw=np.mean(raw_video[:,:,0:fnum1], axis=2)
        for i in range(fnum1):
            CC_raw[0,i]=cv2.matchTemplate(raw_video[int(max_y_shift):int(height1-max_y_shift), int(max_x_shift):int(width1- max_x_shift),i],
                                          template_raw[int(max_y_shift):int(height1-max_y_shift), int(max_x_shift):int(width1- max_x_shift)], cv2.TM_CCOEFF_NORMED)

        height2 = fixed_video.shape[0]
        width2 = fixed_video.shape[1]
        fnum2 = fixed_video.shape[2]
        CC_fixed = np.empty([1, fnum1])
        template_fixed = np.mean(fixed_video[:, :, 0:fnum2], axis=2)
        for i in range(fnum2):
            CC_fixed[0, i] = cv2.matchTemplate(fixed_video[int(max_y_shift):int(height2-max_y_shift), int(max_x_shift):int(width2- max_x_shift),i],
                                               template_fixed[int(max_y_shift):int(height2-max_y_shift), int(max_x_shift):int(width2- max_x_shift)], cv2.TM_CCOEFF_NORMED)

        x = np.linspace(1, fnum1, fnum1)
        CC_raw=np.squeeze(CC_raw, axis=0)
        CC_fixed=np.squeeze(CC_fixed, axis=0)
        plt.plot(x, CC_raw, label='raw video')
        plt.plot(x, CC_fixed, label='NCC fixed video')
        plt.legend()
        plt.xlabel('Frames')
        plt.title('CC of each frame and template')
        plt.show()

    def WriteVideo(self, video):
        fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
        out = cv2.VideoWriter('fixed_video.avi', fourcc, 20, (int(video.shape[1]), int(video.shape[0])))
        for i in range(video.shape[2]):

            frame = video[:, :, i]
            frame = frame.astype(np.uint8)
            #cv2.imshow('video', frame)
            out.write(frame)

        out.release()







