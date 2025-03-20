import os
import cv2
import json
import argparse
import numpy as np
from tqdm import tqdm


def make_labels(root_dir: str, extension: str = ".jpg") -> None:
    """_summary_

    Args:
        root_dir (str): base dir
        extension (str, optional): image extension at images/. Defaults to ".jpg".
    """

    dump_dir = root_dir.replace("segmentations", "labels")
    image_dir = root_dir.replace("segmentations", "images")

    # get all directories in root dir
    directories = [os.path.join(root_dir, d) for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))]

    for target_dir in tqdm(directories):
        frame_name = int(os.path.basename(target_dir)) + 1
        frame_name = f"frame_{str(frame_name).zfill(5)}"
        tqdm.write(frame_name)
        # initalization
        json_data = {}
        objects = []

        for idx, filename in enumerate(os.listdir(target_dir)):
            if filename.endswith(".png"):
                tqdm.write(os.path.splitext(filename)[0])
                image_path = os.path.join(target_dir, filename)
                
                mask = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                _, binary = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                obj_info = {
                    "category": os.path.splitext(filename)[0],
                    "group": int(idx),
                    "segmentation": [],
                    "area": 0,
                    "layer": float(idx),
                    "bbox": [],
                    "iscrowd": 0,
                    "note": ""
                }                

                if contours:
                    largest_contour = max(contours, key=cv2.contourArea)
                    segmentation = [[float(pt[0][0]), float(pt[0][1])] for pt in largest_contour]
                    obj_info["segmentation"] = segmentation
                    obj_info["area"] = float(cv2.contourArea(largest_contour))
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    obj_info["bbox"] = [float(x), float(y), float(w), float(h)]
                
                objects.append(obj_info)

        # add image info.
        json_data["info"] = {
            "name": f"{frame_name}.jpg",
            "width": mask.shape[1],
            "height": mask.shape[0],
            "depth": 3,
            "note": ""
        }
        json_data["objects"] = objects

        # Dump json file and copy image
        os.makedirs(dump_dir, exist_ok=True)
        json_path = os.path.join(dump_dir, f"{frame_name}.json")
        with open(json_path, "w") as f:
            json.dump(json_data, f, indent=4)

        tqdm.write(f"Dump json file at: {json_path}")

        image_path_base = os.path.join(image_dir, f"{os.path.basename(target_dir)}.{extension}")
        image_path_target = os.path.join(dump_dir, f"{frame_name}.jpg")

        if os.path.exists(image_path_base):
            tqdm.write(f"Copy image {image_path_base} -> {image_path_target}")
            cv2.imwrite(image_path_target, cv2.imread(image_path_base))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate labels from segmentations.")
    parser.add_argument("--input_dir", "-i", type=str, required=True, help="Path to the root directory of segmentations.")
    parser.add_argument("--extension", type=str, default=".jpg", help="Path to the root directory of segmentations.")
    args = parser.parse_args()

    root_dir = args.input_dir
    make_labels(root_dir=root_dir, extension=args.extension)
