# Instructions

## Requirements:

Install and activate conda environment
```
conda env create -f environment.yml
conda activate vps_training
```

## Recording

TODO: Record data from femto and oak

## Preprocessing

Create poses for orbbec dataset
```
cd preprocessing
python mapping_femto.py /path/to/recordings/orbbec
```

Create poses for oak stereo left dataset
```
python mapping_oakd.py /path/to/recordings/oak
```


Add poses of femto to oak and align images 
```
python3 add_ground_truth.py orbbec/2 oak/2
```

Extract all rgb frames from the original stereo left  video at 30 fps

```
ffmpeg -i oak/1/data2.mkv -vf "fps=30" -start_number 0
oak/1/fps30/%d.png
```
 
Extract poses from jsonl and save as individual txt files. It will copy needed original images to a new folder and extract poses for those images.
```
python extract_oak_femto_poses.py
```

Create calibration files for each png file.
```
python calib_file.py
```
        
Separate all files into train and test sets. Each should have rgb, poses and calibration folders
Delete unneeded files in: images, poses, calibration files

## Training
For more details on training and test see the original repository https://github.com/vislearn/dsacstar/

```
cd dsacstar
source activate dsacstar
```

Extract the tar file from dsacstar/models/7scenes_office_rgb.tar.xz, and initialize train_init.py with pretrained model (already added in the code)
```
python train_init.py scene6 model --mode 0
```

Train part 2
```
python train_e2e.py scene6 model_epoch_160.net model_e2e_160 --mode 1
```

## Testing
```
python test.py scene6 model_epoch_1000.net --mode 1 
python test.py scene6 model_e2e_160_epoch_100.net --mode 1
```

## Extra scripts

Find the intrinsics of the camera or it is written in calibration.json file. Use focal length = 565 for oak stereo camera.
```
python data_preprocessing/calibration.py
```

If needed, calculate mean and standard deviation for a new dataset using 
```
python data_preprocessing/mean_std.py
```

