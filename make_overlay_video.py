#!/usr/bin/env python 
import os.path 
import os
from glob import glob 

name = 'hydra1'
#name = 'hydra_neurons1'
#name = 'square3_gradient_texture'
#name = 'square2_gradient'
#name = 'square1'
#ff = 'translate_leftup_stretch'
#ff = 'translate_leftup'
ff = 'warp'
#ff = 'rotate'
notes = 'masked_iekf_multi'

#Output
#img_in = './synthetictests/' + name + '/' + ff + '_' + notes + '_pred/'
#vid_out = './synthetictests/' + name + '/' + ff + '_' + notes + '_pred/video/'

#img_in = './testruns/default_johntest_short/'
#vid_out = './testruns/default_johntest_short/video/'

#img_in = './screenshots/johntest_brightcontrast_short_lengthadapt_frame/'
#vid_out = './testruns/lengthadapt4_johntest_short/'

img_in = './mfsf_output/stack0002_nref100/mesh/'
vid_out = './mfsf_output/stack0002_nref100/mesh_overlay/'

#Make video directory
if not os.path.isdir(vid_out):
	os.makedirs(vid_out)

#Find all files and mv according to name
for idx,fn in enumerate(sorted(glob(img_in + '*overlay*.png'))):
	print 'Moving', idx,fn
	#print 'mv ' + fn + ' ' + vid_out + 'overlay_%00d.png'%idx
	os.system('mv ' + fn + ' ' + vid_out + 'overlay_%03d.png'%idx) 

#Call ffmpeg to make video
avconv = 'avconv -framerate 5 -i ' + vid_out + 'overlay_%03d.png -c:v huffyuv -y'
os.system(avconv + ' ' + vid_out + 'output.avi')



#Will display frame number too...??
#-vf "drawtext=fontfile=Arial.ttf: text=%{n}: x=(w-tw)/2: y=h-(2*lh): fontcolor=white: box=1: boxcolor=0x00000099"