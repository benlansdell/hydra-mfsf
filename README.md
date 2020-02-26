# HydraMFSF
Python code for Hydra optical flow, behavior and neural analysis.

Analysis of MFSF (multi-frame subspace constrained optic flow -- http://www0.cs.ucl.ac.uk/staff/lagapito/subspace_flow/) tracking of Hydra body/neurons.

lansdell 2016

Dependencies:
* Vispy*
* Numpy
* PyCuda**
* DistMesh 
* OpenCV2
* cvtools (https://github.com/benlansdell/cvtools)
* matplotlib

Notes:
* *Uses OpenGL rendering. If using remotely, you'll need to set up a VirtualGL server
* **If have a CUDA compatible graphics card

![alt tag](https://github.com/benlansdell/hydra-mfsf/blob/master/hydra_tracked.png)

# Pipeline

This codebase does many things related to tracking the Hydra body position throughout an extended video.

The steps involved in the pipeline can be found in process_tiff.py, which will work through the preprocessing and processing of a tiff file. The steps are:
Will do the following, given [tiff_file] and [name]:
1. Split a large tiff into 250 frame parts, save in ../hydra/video/[name] by default
2. Run MFSF method, forward and backward. Will save in ./mfsf_output/[name]
3. Copy interframes for their own processing.
4. Have the user select the reference frames to use.
5. Run DeepMatching and DeepFlow between all interframes and the reference frames
6. Compute MFSF error terms
7. Perform MS image segmentation, using combination of MFSF derived error terms and DM error terms. This gives us the mappings between the interframes and the reference frames for each block. 
8. Perform continuation (currently this needs OpenGL, annoying to use remotely)
Final step: render the tracking as meshes moved through the video.

This is still a work in progress, and it may be better to treat process_tiff.py as a template for a script to work through your particular dataset.

# References
[1] Ravi Garg, Anastasios Roussos, Lourdes Agapito, "A Variational Approach to Video Registration with Subspace Constraints", International journal of computer vision 104 (3), 286-314, 2013 
