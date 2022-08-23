from django.core.files import File
from pathlib import Path
from PIL import Image
from io import BytesIO


def image_resize(image, width, height):
    # Open the image using Pillow
    img = Image.open(image)
    # check if either the width or height is greater than the max
    if img.width > width or img.height > height:
        output_size = (width, height)

        img_width, img_height = img.size
        new_size = min(img_width, img_height)
        left = (img_width - new_size)/2
        top = (img_height - new_size)/2
        right = (img_width + new_size)/2
        bottom = (img_height + new_size)/2

        # Crop the image using the Pillow Image object
        img = img.crop((left, top, right, bottom))

        # Create a new resized “thumbnail” version of the image with Pillow
        img.thumbnail(output_size)
        # Find the file name of the image
        img_filename = Path(image.file.name).name

        filename_without_extension = img_filename.split(".")[0]

        img_filename = filename_without_extension + ".jpg"

        buffer = BytesIO()
        img.convert('RGB').save(buffer, format='JPEG')
        # Wrap the buffer in File object
        file_object = File(buffer)
        # Save the new resized file as usual, which will save to S3 using django-storages
        image.save(img_filename, file_object)
