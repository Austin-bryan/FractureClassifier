"""
This file focuses on augmenting the training split using albumentations and cv2.

It takes the original images and labels, applies augmentations,
and saves the augmented images and labels in a new directory structure.
"""

import os  # for file handling
import cv2  # for image processing
import albumentations as A  # for data augmentation

# Not needed (for now)
# import random  # for shuffling data
# import shutil  # for copying files
# import numpy as np  # for numerical operations
# import matplotlib.pyplot as plt  # for visualizing augmented images and labels

# import tensorflow as tf  # for deep learning operations
# import tensorflow.keras as keras  # for building and training neural networks
# # for defining layers in the neural network
# from tensorflow.keras import layers


# Main functions

def load_yolo_labels(label_path):
    """
    This function reads a YOLO format label
    and extracts the class labels and bounding boxes.
    Args:
    label_path (str): The path to the label file in YOLO format
    Returns:
    class_labels (list of int): A list of class labels corresponding to the bounding boxes
    bboxes (list of tuples): A list of bounding boxes in YOLO format (x_center, y_center, width, height)
    """
    bboxes = []  # list to store bounding boxes
    class_labels = []  # list to store class labels

    if not os.path.exists(label_path):  # check if label file exists
        return class_labels, bboxes

    with open(label_path, 'r') as f:  # open the label file for reading
        for line in f:  # reads each line in the file
            parts = line.strip().split()
            if len(parts) != 5:  # if the line does not have exactly 5 parts, skip it
                continue
            class_id = int(parts[0])  # class id part of the line
            x_center = float(parts[1])  # x center of the bbox
            y_center = float(parts[2])  # y center of the bbox
            width = float(parts[3])  # width of the bbox
            height = float(parts[4])  # height of the bbox

            class_labels.append(class_id)
            bboxes.append((x_center, y_center, width, height))

    return class_labels, bboxes


def save_yolo_labels(label_path, class_labels, bboxes):
    """
    This function saves the class labels
    and bounding boxes in YOLO format to a label file.

    Args:
    label_path (str): The path to the label file where the augmented labels will be saved
    class_labels (list of int): A list of class labels corresponding to the bounding boxes
    bboxes (list of tuples): A list of bounding boxes in YOLO format (x_center, y_center, width, height)
    """
    with open(label_path, 'w') as f:  # open the label file for writing
        for class_id, bbox in zip(class_labels, bboxes):
            x_center, y_center, width, height = bbox
            # write the class id and bbox to the file
            print(
                f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}", file=f)


def get_augmentation_pipeline():
    """
    This function defines the augmentation pipeline using albumentations.
    It includes horizontal flips, rotations, affine transformations,
    and brightness/contrast adjustments.

    Args:
    Returns:
        A.Compose: The defined augmentation pipeline.
    """
    return A.Compose(
        [
            # A.HorizontalFlip(p=0.5),
            # Border mode replicate to avoid black borders after rotation
            # A.Rotate(limit=10, border_mode=cv2.BORDER_REPLICATE, p=0.5),
            A.Affine(  # small random affine transformations to simulate different perspectives
                scale=(0.9, 1.1),
                # small translation to avoid losing too much of the image
                translate_percent=(0.0, 0.05),
                rotate=0,  # no additional rotation
                shear=0,  # no need to distort the boxes
                fit_output=False,  # keep the original image size
                p=0.5  # apply affine transformation with 50% probability
            ),
            A.RandomBrightnessContrast(  # adjust brightness and contrast to simulate different lighting conditions
                brightness_limit=0.15,  # avoid making the image too dark or too bright
                contrast_limit=0.15,  # avoids drastic contrast changes
                p=0.4
            ),
            # invert colors with a low probability
            A.InvertImg(p=0.1),
            # apply Gaussian blur to simulate motion blur or out-of-focus images
            A.GaussianBlur(blur_limit=(3, 7), p=0.2)
        ],
        bbox_params=A.BboxParams(  # specify the bounding boxes in YOLO format and how to handle them during augmentation
            format="yolo",
            label_fields=["class_labels"],
            min_visibility=0.3  # only keep boxes with 30% visibility after augmentation
        )
    )


def augment_image_and_boxes(image, bboxes, class_labels, transform):
    """
    This function applies the augmentation pipeline to an image
    and its corresponding bounding boxes and class labels.
    It returns the augmented image, bounding boxes, and class labels.

    Args:
    image (numpy array): The input image to be augmented.
    bboxes (list of tuples): A list of bounding boxes in YOLO format (x_center, y_center, width, height).
    class_labels (list of int): A list of class labels corresponding to the bounding boxes.
    transform (albumentations.Compose): The augmentation pipeline.
    """
    augmented = transform(
        image=image,
        bboxes=bboxes,
        class_labels=class_labels
    )

    # Extract the augmented image, bounding boxes, and class labels from the augmented result
    aug_image = augmented["image"]
    aug_bboxes = augmented["bboxes"]
    aug_class_labels = augmented["class_labels"]
    return aug_image, aug_bboxes, aug_class_labels


def process_train_folder(images_dir, labels_dir, num_augments=2):
    """
    process_train_folder is the main function that processes the training folder
    by applying augmentations to the images and their corresponding labels.

    It takes in the directory paths for images and labels, as well as the number of augmentations to apply to each image.
    The function reads each image and its corresponding label, applies the defined augmentation pipeline,
    and saves the augmented images and labels in a new directory structure.

    Args:
        images_dir (_type_):
        labels_dir (_type_):
        num_augments (int, optional): The number of augmentations to apply to each image. Defaults to 2.
    """

    # get the defined augmentation pipeline
    transform = get_augmentation_pipeline()

    if not os.path.exists(images_dir):
        print(f"Error: Images directory not found: {images_dir}")
        return

    if not os.path.exists(labels_dir):
        print(f"Error: Labels directory not found: {labels_dir}")
        return

    valid_exts = (".png", ".jpg", ".jpeg")  # valid image extensions
    image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(
        valid_exts)]  # list of image files in the directory

    for image_name in image_files:  # iterate through image files
        # gets the full path of the image
        image_path = os.path.join(images_dir, image_name)
        # gets the filestem (filename without extension)
        stem = os.path.splitext(image_name)[0]
        label_path = os.path.join(labels_dir, stem + ".txt")

        # cv2 is used to read the image from the path
        image = cv2.imread(image_path)
        if image is None:  # if the image cannot be read, skip it
            print(f"Warning: Could not read image {image_path}. Skipping.")
            continue

        # load the corresponding labels for the image
        class_labels, bboxes = load_yolo_labels(label_path)

        # Skip unlabeled images for positive fracture augments
        # if len(bboxes) == 0:
        #     continue

        for i in range(num_augments):  # apply augmentations to the image and labels
            try:
                aug_image, aug_bboxes, aug_class_labels = augment_image_and_boxes(
                    image, bboxes, class_labels, transform)

                # Save the augmented image and labels

                # create a new name for the augmented image
                aug_image_name = f"{stem}_aug_{i}.jpg"
                # create a new name for the augmented label
                aug_label_name = f"{stem}_aug_{i}.txt"

                # get the path to save the augmented image
                aug_image_path = os.path.join(images_dir, aug_image_name)
                # get the path to save the augmented label
                aug_label_path = os.path.join(labels_dir, aug_label_name)

                # save the augmented image to disk
                cv2.imwrite(aug_image_path, aug_image)
                # save the augmented labels to disk
                save_yolo_labels(aug_label_path, aug_class_labels, aug_bboxes)

            except Exception as e:
                print(f"Failed on {image_name} with error: {e}")


if __name__ == "__main__":
    train_images_dir = "data/images/train"  # directory for training images
    train_labels_dir = "data/labels/train"  # directory for training labels

    # process the training folder with augmentations
    process_train_folder(train_images_dir, train_labels_dir, num_augments=2)
    print("Data augmentation completed successfully.")
