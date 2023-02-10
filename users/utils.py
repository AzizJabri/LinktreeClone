from PIL import Image
import io
import cloudinary


def resize_image(image_field, height, width):
    # Open the image file
    image = Image.open(image_field)

    # Resize the image
    image = image.resize((width, height), Image.ANTIALIAS)

    # Save the resized image to a memory buffer
    image_buffer = io.BytesIO()
    image.save(image_buffer, format=image.format)
    image_buffer.seek(0)

    # Generate the URL for the resized image
    cloudinary_url = cloudinary.CloudinaryImage(image_field.path).build_url(
        transformation=[{"width": width, "height": height, "crop": "fill"}]
    )

    return cloudinary_url
