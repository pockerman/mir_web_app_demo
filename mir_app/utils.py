from pathlib import Path
import os
from typing import List


def create_survey_directory(directory_path: Path, survey_id: str):
    if not os.path.exists(directory_path / survey_id):
        os.makedirs(directory_path / survey_id)
    else:
        raise ValueError("Could not create directory. The directory={0} exist".format(directory_path / survey_id))


def save_image(image_file, filepath: Path):
    with open(filepath, 'wb+') as destination:
        for chunk in image_file.chunks():
            destination.write(chunk)


def count_number_of_files(filepath: Path, postfix: List[str]):

    """Get the image files in the given image directory that have
    the specified image format.
    Parameters
    ----------
    img_dir: The image directory
    img_formats: The image formats
    Returns
    -------
    An instance of List[Path]
    """

    # load the corrosion images
    img_files = os.listdir(filepath)

    files: List[Path] = []

    for filename in img_files:
        if os.path.isfile(filepath / filename) and filename.split(".")[-1].lower() in postfix:
            files.append(filepath / filename)

    return files

