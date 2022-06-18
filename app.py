import xml.etree.ElementTree as ET
from os import listdir
from os.path import isfile, join
from classes import Category, Ima, Annotation
from PIL import Image
import json
import argparse


def check_resize_save_img(
    filename,
    width,
    height,
    images_folder,
    final_images_folder,
    MAX_SIZE=(800, 450),
):
    image_file = Image.open(join(images_folder, filename))
    width = int(width)
    height = int(height)
    resize = False
    if width > 800:
        resize = True
    if height > 450:
        resize = True
    if resize:
        image_file.thumbnail(MAX_SIZE, Image.ANTIALIAS)
        size = image_file.size
        x_ratio = size[0] / width
        y_ratio = size[1] / height
        ratio = (x_ratio, y_ratio)
    else:

        size = (width, height)
        ratio = (1, 1)
    image_file.save(join(final_images_folder, filename), "JPEG")
    return ratio, size


def parseXML(xml_foler, images_folder, final_images_folder):

    catId = 0
    imageId = 0
    annId = 0

    categories = []
    images = []
    annoations = []

    cat_names = []

    files = [f for f in listdir(xml_foler) if isfile(join(xml_foler, f))]
    for file in files:
        tree = ET.parse(join(xml_foler, file))

        # Parse image data
        imageId += 1
        width = tree.findall(".//width")[0].text
        height = tree.findall(".//height")[0].text
        filename = tree.findall(".//filename")[0].text
        curr_ratio, curr_size = check_resize_save_img(
            filename, width, height, images_folder, final_images_folder
        )
        img = Ima(imageId, curr_size[0], curr_size[1], filename)
        images.append(img)

        names = tree.findall(".//name")
        xmins = tree.findall(".//xmin")
        ymins = tree.findall(".//ymin")
        xmaxs = tree.findall(".//xmax")
        ymaxs = tree.findall(".//ymax")

        for name, xmin, ymin, xmax, ymax in zip(names, xmins, ymins, xmaxs, ymaxs):
            if name.text in cat_names:
                for cat in categories:
                    if cat.get_name() == name.text:
                        curr_cat = cat.get_id()
                        break
            else:
                catId += 1
                curr_cat = catId
                cat = Category(catId, name.text)
                categories.append(cat)
                cat_names.append(name.text)

            xmin = int(xmin.text) * curr_ratio[0]
            xmax = int(xmax.text) * curr_ratio[0]
            ymin = int(ymin.text) * curr_ratio[1]
            ymax = int(ymax.text) * curr_ratio[1]
            w = xmax - xmin
            h = ymax - ymin

            annId += 1
            ann = Annotation(annId, imageId, curr_cat, [xmin, ymin, w, h])
            annoations.append(ann)

    return images, categories, annoations


parser = argparse.ArgumentParser()
parser.add_argument("imagedir")
parser.add_argument("xmldir")
parser.add_argument("outputdir")
args = parser.parse_args()


images_folder = args.imagedir
xml_foler = args.xmldir
final_images_folder = args.outputdir

images, categories, annotations = parseXML(
    xml_foler, images_folder, final_images_folder
)

d = dict()


dicts = []
for c in categories:
    d1 = dict()
    d1["id"], d1["name"], d1["supercategory"] = c.get_data()
    dicts.append(d1)
d["cagetories"] = dicts

dicts = []
for i in images:
    d1 = dict()
    d1["id"], d1["width"], d1["height"], d1["file_name"] = i.get_data()
    dicts.append(d1)
d["images"] = dicts

dicts = []
for a in annotations:
    d1 = dict()
    d1["id"], d1["image_id"], d1["category_id"], d1["bbox"] = a.get_data()
    dicts.append(d1)
d["annotations"] = dicts


with open("output.json", "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=4)
