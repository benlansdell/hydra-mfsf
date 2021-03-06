#!/usr/bin/env python
import sys, os
import argparse

import xml.etree.ElementTree as ET

from os.path import abspath 
from glob import glob 

from xlrd import open_workbook
import cPickle as pickle

import numbers 
import timeit

def parseSheet(sheet):
	tracks = {}
	currenttrack = []
	ntracks = 0
	nR = sheet.nrows
	for r in range(nR):
		row = sheet.row(r)
		if len(row[0].value) > 0:		
			#Start a new track
			if len(currenttrack):
				tracks[ntracks] = currenttrack
				ntracks += 1
			currenttrack = []
		elif isinstance(row[2].value, numbers.Number):
			#Add to current track
			x = row[3].value
			y = row[4].value
			t = row[2].value
			pt = [x, y, t]
			currenttrack.append(pt)
	return tracks 

def main():
	usage = """icy_particletracker.py [frames_in] [fn_out] -maxfiles MAXFILES -runtime RUNTIME

	Run particle tracking method on series of tif files using bioimage analysis
	program Icy. Calls program at the command line. 
		
	Ben Lansdell
	02/22/2017
	"""
	
	icypath = '/home/lansdell/local/icy2/'
	protocol = 'spottracking_headless.xml'

	parser = argparse.ArgumentParser()
	parser.add_argument('frames_in', help='path to .tif files, will use all tif files in folder')
	parser.add_argument('fn_out', help='output filename for python dictionary of tracks')
	parser.add_argument('-maxfiles', help='maximum number of tif files to read', default=250)
	parser.add_argument('-runtime', help='if provided will store time in seconds Icy took to run', default=None)
	args = parser.parse_args()

	runtime = args.runtime
	mf = int(args.maxfiles)
	fn_out = args.fn_out
	frames_in = args.frames_in
	fin = [abspath(p) for p in sorted(glob(frames_in + '*.tif'))]
	fin = fin[0:mf]
	frames = ':'.join(fin)

	xls_in = frames.split(':')[0] + '_tracking.xls'
	os.system('rm %s'%xls_in)

	#Edit .xml protocol with input tif files
	tree = ET.parse(icypath + protocol)
	root = tree.getroot()
	infiles = root.find('blocks').find('block').find('variables').find('input').find('variable')
	infiles.set('value', frames)
	tree.write(icypath + protocol)

	print '\n=============================='
	print 'Running Icy particle tracking:'
	print '==============================\n'

	starttime = timeit.default_timer()
	cmd = 'cd %s; java -jar icy.jar --headless --execute plugins.adufour.protocols.Protocols protocol=%s/%s'%(icypath, icypath, protocol)
	os.system(cmd)
	elapsed = timeit.default_timer() - starttime

	print '\n=============================='
	print '...done in %f seconds.'%elapsed

	print 'Saving results to python dictionary'
	wb = open_workbook(xls_in)
	sheet = wb.sheet_by_name('Tracks')
	tracks = parseSheet(sheet)
	pickle.dump(tracks, open(fn_out, 'wb'))

	#Also save a csv file
	fh = open(split(fn_out, '.')[0:-1]+'.csv', 'w')
	for n_id in tracks:
		for [x,y,frame] in tracks[n_id]:
			fh.write("%d,%d,%d,%d\n"%(n_id, frame, x, y))
	fh.close()

	if runtime:
		with open(runtime, 'a') as fh:
			fh.write('%d,%f\n'%(mf, elapsed))

if __name__ == "__main__":
	sys.exit(main())