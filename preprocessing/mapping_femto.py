import spectacularAI
import cv2
import json
import os

# KeyFrames for which we've already saved the image
savedKeyFrames = {}
visualizer = None

def deleteFramesWithoutPose(output):
    imageDirectory = os.path.join(args.output, "images")
    for filename in os.listdir(imageDirectory):
        if filename.split('.')[1] != "png": continue
        frameId = int(filename.split('_')[1].split('.')[0])
        if frameId in output.map.keyFrames: continue
        filepath = os.path.join(imageDirectory, filename)
        print("deleted ", filepath)
        os.remove(filepath)

def saveAsPng(outputFolder, frameId, cameraName, frame, grayscale=False):
    if not frame or not frame.image: return
    fileName = outputFolder + "/" + cameraName + "_" + f'{frameId:05}' + ".png"
    try:
        cv2.imwrite(fileName, cv2.cvtColor(frame.image.toArray(), cv2.COLOR_GRAY2BGR if grayscale else cv2.COLOR_RGB2BGR))
    except Exception as e:
        print(f"Error writing PNG: {e}")
        raise

def onVioOutput(output):
    if visualizer is not None:
        visualizer.onVioOutput(output.getCameraPose(0), status=output.status)

def onMappingOutput(output):
    if visualizer is not None:
        visualizer.onMappingOutput(output)

    if output.finalMap:
        # Final optimized poses, let's save them to jsonl file
        with open(args.output + "/poses.jsonl", "w") as outFile:
            for frameId in output.map.keyFrames:
                keyFrame = output.map.keyFrames.get(frameId)
                outputJson = {
                    "frameId": frameId,
                    "poses": {}
                }

                frameSet = keyFrame.frameSet
                rgbFrame = frameSet.rgbFrame
                if rgbFrame is None: continue

                print(rgbFrame)
                # In aligned RGB-D mode, the distorted rgb camera pose == undistorted rgb camera pose == aligned depth camera pose
                outputJson["poses"]["rgb"] = rgbFrame.cameraPose.getCameraToWorldMatrix().tolist()
                outputJson["poses"]["depth"] = rgbFrame.cameraPose.getCameraToWorldMatrix().tolist()
                outFile.write(json.dumps(outputJson) + "\n")
        deleteFramesWithoutPose(output)
        print("Saved optimized key frame poses")
    else:
        # New frames, let's save the images to disk
        for frameId in output.updatedKeyFrames:
            keyFrame = output.map.keyFrames.get(frameId)
            if not keyFrame or savedKeyFrames.get(frameId): continue # deleted key frame, or we already saved the images
            savedKeyFrames[frameId] = True

            frameSet = keyFrame.frameSet
            rgbFrame = frameSet.rgbFrame
            depthFrame = frameSet.depthFrame

            if rgbFrame is None or rgbFrame.image is None: continue
            if depthFrame is None or depthFrame.image is None: continue

            # compute undistorted rgb, and align depth to the undistorted rgb frame
            undistortedRgb = frameSet.getUndistortedFrame(rgbFrame)
            alignedDepth = frameSet.getAlignedDepthFrame(undistortedRgb)
            # Note: if you need camera intrinsics from undistorted camera, get them here
            # intrinsics = undistortedRgb.cameraPose.camera.getIntrinsicMatrix()

            # save images
            saveAsPng(os.path.join(args.output, "images"), frameId, "rgb", undistortedRgb)
            saveAsPng(os.path.join(args.output, "images"), frameId, "depth", alignedDepth, True)

def parseArgs():
    import argparse
    p = argparse.ArgumentParser(__doc__)
    p.add_argument("input", help="Folder containing the recorded session for mapping")
    p.add_argument("output", help="Output folder for key frame images and their poses ", nargs="?", default="output")
    p.add_argument("--fast", help="Use default settings (faster, lower quality)", action="store_true")
    p.add_argument("--preview", help="Enable visualization", action="store_true", default=False)
    return p.parse_args()

if __name__ == '__main__':
    args = parseArgs()
    os.makedirs(os.path.join(args.output, "images"), exist_ok=True)

    if not args.fast:
        # Offline parameters for Orbbec Femto devices
        config = {
            "maxMapSize": 0, # Unlimited SLAM map size 
            "keyframeDecisionDistanceThreshold": 0.05, 
            "icpVoxelSize": 0.05, 
            "maxKeypoints": 1000, 
            "optimizerMaxIterations": 30, 
            "parameterSets": ["wrapper-base", "point-cloud", "offline-base", "orbbec-femto", "icp", "offline-icp"],
            "mapSavePath": os.path.join(args.output, "pointcloud.ply")
        }
        replay = spectacularAI.Replay(args.input, mapperCallback=onMappingOutput, configuration=config, ignoreFolderConfiguration=True)
    else:
        config = {"mapSavePath": os.path.join(args.output, "pointcloud.ply")}
        replay = spectacularAI.Replay(args.input, mapperCallback=onMappingOutput, configuration=config)

    if args.preview:
        from spectacularAI.cli.visualization.visualizer import Visualizer, VisualizerArgs, ColorMode
        visArgs = VisualizerArgs()
        visArgs.targetFps = 30
        visArgs.colorMode = ColorMode.NORMAL
        visualizer = Visualizer(visArgs)
        replay.setOutputCallback(onVioOutput)
        replay.startReplay()
        visualizer.run()
        replay.close()
    else:
        replay.runReplay()
