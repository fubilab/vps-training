import argparse
import spectacularAI
import cv2
import json
import os

p = argparse.ArgumentParser(__doc__)
p.add_argument("input", help="Folder containing the recorded session for mapping")
p.add_argument("output", help="Output folder for key frame images and their poses ", default="output")
p.add_argument("--preview", help="Show latest primary image as a preview", action="store_true")
p.add_argument("--no_preview3d", help="Disable visualization", action="store_true")

args =  p.parse_args()

# KeyFrames for which we've already saved the image
savedKeyFrames = {}

visualizer = None

def saveAsPng(output, frameId, cameraName, frame):
    if not frame or not frame.image: return
    fileName = output + "/" + cameraName + "_" + f'{frameId:05}' + ".png"
    cv2.imwrite(fileName, cv2.cvtColor(frame.image.toArray(), cv2.COLOR_RGB2BGR))

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
                if frameSet.primaryFrame: outputJson["poses"]["primary"] = frameSet.primaryFrame.cameraPose.getCameraToWorldMatrix().tolist()
                if frameSet.secondaryFrame: outputJson["poses"]["secondary"] = frameSet.secondaryFrame.cameraPose.getCameraToWorldMatrix().tolist()
                if frameSet.rgbFrame: outputJson["poses"]["rgb"] = frameSet.rgbFrame.cameraPose.getCameraToWorldMatrix().tolist()
                if frameSet.depthFrame: outputJson["poses"]["depth"] = frameSet.depthFrame.cameraPose.getCameraToWorldMatrix().tolist()
                outFile.write(json.dumps(outputJson) + "\n")
    else:
        # New frames, let's save the images to disk
        for frameId in output.updatedKeyFrames:
            keyFrame = output.map.keyFrames.get(frameId)
            if not keyFrame or savedKeyFrames.get(frameId): continue
            savedKeyFrames[frameId] = True
            frameSet = keyFrame.frameSet
            saveAsPng(args.output, frameId, "primary", frameSet.primaryFrame)
            saveAsPng(args.output, frameId, "secondary", frameSet.secondaryFrame)
            saveAsPng(args.output, frameId, "rgb", frameSet.rgbFrame)
            saveAsPng(args.output, frameId, "depth", frameSet.depthFrame)
            if args.preview and frameSet.primaryFrame.image:
                cv2.imshow("Primary camera", cv2.cvtColor(frameSet.primaryFrame.image.toArray(), cv2.COLOR_RGB2BGR))
                cv2.setWindowTitle("Primary camera", "Primary camera #{}".format(frameId))
                cv2.waitKey(1)

os.makedirs(args.output)

# Parameters copied from https://github.com/SpectacularAI/sdk/blob/main/python/cli/process/process.py
config = {
    'maxMapSize': 0,
    'keyframeDecisionDistanceThreshold': 0.05,
    'maxKeypoints': 1000,
    'optimizerMaxIterations': 30,
    'stereoPointCloudMinDepth': 0.5,
    'alreadyRectified': True,
    'parameterSets': ['wrapper-base', 'offline-base', 'oak-d']
}

replay = spectacularAI.Replay(args.input, mapperCallback=onMappingOutput, configuration=config, ignoreFolderConfiguration=True)
if args.no_preview3d:
    replay.runReplay()
else:
    from spectacularAI.cli.visualization.visualizer import Visualizer, VisualizerArgs
    visArgs = VisualizerArgs()
    visArgs.targetFps = 30
    visualizer = Visualizer(visArgs)
    replay.setOutputCallback(onVioOutput)
    replay.startReplay()
    visualizer.run()
    replay.close()
