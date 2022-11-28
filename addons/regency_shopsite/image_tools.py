import io
from collections import namedtuple
from tempfile import TemporaryFile
from base64 import b64encode, b64decode

from PIL import UnidentifiedImageError, Image, EpsImagePlugin #EpsImagePlugin needed for read eps files
from PyPDF2 import PdfFileReader
from PyPDF2.utils import PdfReadError
from pdf2image import convert_from_bytes
from pdf2image.exceptions import PDFSyntaxError, PDFPageCountError
from cairosvg import svg2png
from xml.etree.ElementTree import ParseError, parse
from werkzeug.datastructures import FileStorage
from odoo.exceptions import ValidationError

from odoo.addons.regency_shopsite.const import PDF_FILE_FORMATS, EPS_FILE_FORMATS, POSTSCRIPT_FILE_FORMATS, \
    SVG_FILE_FORMATS

ImageType = namedtuple('ImageType', ['is_pdf', 'is_eps', 'is_postscript', 'is_svg'])


def compute_image_data(bytes, type):
    return f'data:{type};base64,{bytes}'


def get_image_types(type):
    return ImageType(
        type in PDF_FILE_FORMATS,
        type in EPS_FILE_FORMATS,
        type in POSTSCRIPT_FILE_FORMATS,
        type in SVG_FILE_FORMATS,
    )


def convert_vector_to_png(file_data, file_type):
    check_type = get_image_types(file_type)

    if not any(check_type._asdict().values()):
        raise ValidationError('File format not supported!')

    file_bytes = b64decode(file_data.encode())
    converted_image = io.BytesIO()

    postscript_is_not_ai = False
    invalid_file_format = False
    if check_type.is_pdf or check_type.is_postscript:
        try:
            images = convert_from_bytes(file_bytes, transparent=True, fmt='png')
            images[0].save(converted_image, 'PNG')
        except (PDFSyntaxError, PDFPageCountError, IndexError):
            if check_type.is_postscript:
                postscript_is_not_ai = True
            else:
                invalid_file_format = True
    if check_type.is_eps or postscript_is_not_ai:
        temp_eps_file = TemporaryFile()
        try:
            temp_eps_file.write(file_bytes)
            eps_file = FileStorage(temp_eps_file, 'temp_eps_file.eps', name='file', content_type=file_type)
            image = Image.open(eps_file)
            image.load(transparency=True)
            image.save(converted_image, format='PNG')
        except UnidentifiedImageError:
            invalid_file_format = True
        temp_eps_file.close()
    if check_type.is_svg:
        try:
            svg2png(bytestring=file_bytes, write_to=converted_image)
        except ParseError:
            invalid_file_format = True

    if invalid_file_format:
        raise ValidationError('Invalid file format!')

    return compute_image_data(b64encode(converted_image.getvalue()).decode(), 'image/png')


def check_if_image_is_vector(image_data, image_type):
    check_type = get_image_types(image_type)

    if not any(check_type._asdict().values()):
        return False

    image_bytes = b64decode(image_data.encode())
    postscript_is_not_ai = False
    if check_type.is_pdf or check_type.is_postscript:
        try:
            PdfFileReader(io.BytesIO(image_bytes))
            return True
        except PdfReadError:
            if check_type.is_postscript:
                postscript_is_not_ai = True
    if check_type.is_eps or postscript_is_not_ai:
        try:
            temp_eps_file = TemporaryFile()
            temp_eps_file.write(image_bytes)
            eps_file = FileStorage(temp_eps_file, 'temp_eps_file.eps', name='file', content_type=image_type)
            Image.open(eps_file)
            temp_eps_file.close()
            return True
        except UnidentifiedImageError:
            pass
    if check_type.is_svg:
        try:
            parse(io.BytesIO(image_bytes))
            return True
        except ParseError:
            pass

    return False
