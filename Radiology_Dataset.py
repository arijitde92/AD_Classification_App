from glob import glob
import numpy as np
import os
from pathlib import Path
import SimpleITK as sitk
import torch
from torch.utils.data import Dataset


def downsamplePatient(patient_CT, height, width, depth):
    """
    A function that downsamples a 3D CT image using SimpleITK library.

    Args:
        patient_CT (str): Path of the input CT image file
        height (int): Desired height of the output image
        width (int): Desired width of the output image
        depth (int): Desired depth of the output image

    Returns:
        sitk.Image: The downsampled CT image as a SimpleITK image object.
    """

    # Read the input CT image using SimpleITK library
    original_CT = sitk.ReadImage(patient_CT, sitk.sitkInt32)

    # Get the dimension, physical size, origin and direction of the original image
    dimension = original_CT.GetDimension()
    reference_physical_size = np.zeros(original_CT.GetDimension())
    reference_physical_size[:] = [(sz - 1) * spc if sz * spc > mx else mx for sz, spc, mx in
                                  zip(original_CT.GetSize(), original_CT.GetSpacing(), reference_physical_size)]
    reference_origin = original_CT.GetOrigin()
    reference_direction = original_CT.GetDirection()

    # Define the reference size and spacing for the downsampled image
    reference_size = [height, width, depth]
    reference_spacing = [phys_sz / (sz - 1) for sz, phys_sz in zip(reference_size, reference_physical_size)]

    # Create a new SimpleITK image with the defined reference size, spacing, origin and direction
    reference_image = sitk.Image(reference_size, original_CT.GetPixelIDValue())
    reference_image.SetOrigin(reference_origin)
    reference_image.SetSpacing(reference_spacing)
    reference_image.SetDirection(reference_direction)

    # Get the center point of the reference image
    reference_center = np.array(
        reference_image.TransformContinuousIndexToPhysicalPoint(np.array(reference_image.GetSize()) / 2.0))

    # Create an affine transformation object for the original image
    transform = sitk.AffineTransform(dimension)
    transform.SetMatrix(original_CT.GetDirection())
    transform.SetTranslation(np.array(original_CT.GetOrigin()) - reference_origin)

    # Create a translation transformation object to center the original image to the reference image center
    centering_transform = sitk.TranslationTransform(dimension)
    img_center = np.array(original_CT.TransformContinuousIndexToPhysicalPoint(np.array(original_CT.GetSize()) / 2.0))
    centering_transform.SetOffset(np.array(transform.GetInverse().TransformPoint(img_center) - reference_center))

    # Apply the affine transformation and centering transformation to the original image
    centered_transform = sitk.Transform(transform)
    final_transform = sitk.CompositeTransform([centered_transform, centering_transform])

    # Resample the original image using the final transformation to get the downsampled image
    return sitk.Resample(original_CT, reference_image, final_transform, sitk.sitkLinear, 0.0)


class RadiologyDataset(Dataset):
    """
    A PyTorch dataset class for 3D CT radiology images.

    Args:
        image_paths (list): A list of paths to the input CT image files
        labels (list): A list of labels for each input image
    """
    def __init__(self, image_paths, labels):
        """
    Initializes the RadiologyDataset class.

    Args:
        image_paths (list of str): A list of file paths to the images.
        labels (list): A list of labels corresponding to each image.

    Returns:
        None.
    """
    self.image_paths = image_paths
    self.labels = labels

    def __len__(self):
        """
        Gets the length of the dataset.

        Args:
            None.

        Returns:
            int: The length of the dataset.
        """
        return len(self.image_paths)

    def __getitem__(self, idx):
        """
        Gets an item from the dataset at the given index.

        Args:
            idx (int): The index of the item to get.

        Returns:
            tuple: A tuple containing the image tensor, the label, and the subject name.
        """
        subject_name = Path(self.image_paths[idx]).stem
        image = downsamplePatient(self.image_paths[idx], 128, 128, 128)
        img = sitk.GetArrayFromImage(image)
        img_tensor = torch.unsqueeze(torch.Tensor(img), 0)
        lbl = self.labels[idx]
        return img_tensor, lbl, subject_name
