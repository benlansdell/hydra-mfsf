#!/usr/bin/env python
import sys, argparse 
from kalman import KalmanFilter
from renderer import VideoStream, FlowStream
from distmesh_dyn import DistMesh

import logging

import pdb 

def main():
	usage = """run_kalmanfilter.py [input_avi_file] [optic_flow_path] [output_avi_file] [threshold]

HydraGL. State space model using an extended Kalman filter to track Hydra in video

Dependencies:
-Vispy*
-Numpy
-PyCuda**
-DistMesh 
-HDF
-OpenCV2
-matplotlib

Notes:
*  Uses OpenGL rendering. If using remotely, you'll need to set up a VirtualGL server
** If have a CUDA compatible graphics card

Example: 
./run_kalmanfilter.py ./video/johntest_brightcontrast_short.avi ... 
 ./video/johntest_brightcontrast_short/flow ./video/output.avi -s 15

For help:
./run_kalmanfilter.py -h 

Ben Lansdell
02/16/2016
"""

	parser = argparse.ArgumentParser()
	parser.add_argument('fn_in', default='./video/johntest_brightcontrast_short.avi', 
		help='input video file, any format readable by OpenCV', nargs = '?')
	parser.add_argument('flow_in', default='./video/johntest_brightcontrast_short/', 
		help='input optic flow path', nargs = '?')
	parser.add_argument('fn_out', default='./video/johntest_brightcontrast_short_output.avi', 
		help='avi output video file', nargs='?')
	parser.add_argument('-n', '--name', default='johntest_brightcontrast_short_lengthadapt', 
		help='name for saving run images', nargs='?')
	parser.add_argument('-t', '--threshold', default=9,
		help='threshold intensity below which is background', type = int)
	parser.add_argument('-s', '--gridsize', default=18,
		help='edge length for mesh (smaller is finer)', type = int)
	parser.add_argument('-c', '--cuda', default=False,
		help='whether or not to do analysis on CUDA', type = bool)
	parser.add_argument('-l', '--logfile', default='./run_kalmanfilter.log',
		help='Output logfile', type = str)
	parser.add_argument('-v', '--level', default=1,
		help='0 == Error, 1 == Info, 2 == Debug', type = int)
	args = parser.parse_args()

	if args.level == 0:
		level = logging.ERROR
	elif args.level == 1:
		level = logging.INFO
	elif args.level == 2:
		level = logging.DEBUG

	print level 

	logging.basicConfig(filename=args.logfile, level=level, \
		format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
	logging.info(' == run_kalmanfilter.py ==\nInitializing...')

	if len(sys.argv) == 1:
		print("No command line arguments provided, using defaults")
		logging.info("No command line arguments provided, using defaults")
	
	logging.info("Generating mesh")
	satisfied = False
	while not satisfied:
		capture = VideoStream(args.fn_in, args.threshold)
		frame = capture.current_frame()
		mask, ctrs, fd = capture.backsub()
		distmesh = DistMesh(frame, h0 = args.gridsize)
		distmesh.createMesh(ctrs, fd, frame, plot = True)
		a = raw_input('Is this mesh ok? Type ''thresh = xx'' to redo threshold and ''grid = xx'' to redo gridsize. Otherwise press ENTER: (currently threshold = %d, gridsize = %d) '%(args.threshold, args.gridsize))
		if len(a) == 0:
			satisfied = True
			break 
		words = a.split('=')
		if len(words) != 2:
			print 'Didn''t understand your response, continuing with current values'
			satisfied = True
		if words[0].strip().lower() == 'thresh':
			args.threshold = int(words[1])
		elif words[0].strip().lower() == 'grid':
			args.gridsize = int(words[1])
		else:
			print 'Didn''t understand your response, continuing with current values'
			satisfied = True

	logging.info("Created mesh")

	#Load flow data from directory
	flowstream = FlowStream(args.flow_in)
	ret_flow, flowframe = flowstream.peek()
	logging.info("Loaded optic flow data")

	if ret_flow:
		#alpha = 0.3
		kf = IteratedMSKalmanFilter(distmesh, frame, flowframe, cuda = args.cuda, sparse = True, multi = True, alpha = 0.01, nI = 4)
		#alpha = 0
		#kf = IteratedMSKalmanFilter(distmesh, frame, flowframe, cuda = args.cuda, sparse = True, multi = True, alpha = 0)
	else:
		print 'Cannot read flow stream'
		return 
	logging.info("Created Kalman Filter, Renderer and CUDA objects")

	#kf.compute(capture.gray_frame(), flowframe)
	logging.info("Starting main loop")

	count = 0
	while(capture.isOpened()):
		count += 1
		print 'Frame %d' % count 
		ret, frame, grayframe, mask = capture.read()
		ret_flow, flowframe = flowstream.read()
		logging.info("Loaded frame %d"%count)

		if ret is False or ret_flow is False:
			break

		kf.compute(grayframe, flowframe, mask, imageoutput = 'screenshots/' + args.name + '_frame_%03d'%count)
		#kf.save(mesh_out)

	logging.info("Streams empty, closing")
	cv2.destroyAllWindows()
	raw_input("Finished. Press enter to exit")

if __name__ == "__main__":
	sys.exit(main())
