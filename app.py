# Importo moduli e libreri
import argparse
import json
import logging
import xml.etree.ElementTree as ET
from os import listdir
from os.path import isfile, join
from PIL import Image
import logging
import warnings

from classes import Category, Ima, Annotation


def check_resize_save_img(
    filename,
    width,
    height,
    images_folder,
    final_images_folder,
    MAX_SIZE=(800, 450),
):
    """
    Funzione per verificare dimensioni immagine, eventualmente modificarla e salvarla

    Args:
        filename: nome file
        width: larghezza img
        height: altezza img
        images_folder: cartella input img
        final_images_folder: cartella output img
        MAX_SIZE : Tupla dimensione max. Defaults to (800, 450).

    Returns:
       Size effettivo e resize_ratio
    """

    # Apro immagine con PIL
    try:
        image_file = Image.open(join(images_folder, filename))
    except Exception as e:
        logging.getLogger("app.py").error("Impossibile aprire immagine ".format(e))
        raise
    width = int(width)
    height = int(height)
    resize = False
    if width > 800 or height > 450:
        resize = True
    if resize:
        # Caso resize
        logging.getLogger("app.py").info("---Resize immagine: {0}".format(filename))
        image_file.thumbnail(MAX_SIZE, Image.ANTIALIAS)
        size = image_file.size
        x_ratio = size[0] / width
        y_ratio = size[1] / height
        ratio = (x_ratio, y_ratio)
    else:
        # Caso no resize
        logging.getLogger("app.py").info(
            "---Non serve resize immagine: {0}".format(filename)
        )
        size = (width, height)
        ratio = (1, 1)
    # in ogni caso salvo immagine in dir output
    try:
        image_file.save(join(final_images_folder, filename), "JPEG")
    except Exception as e:
        logging.getLogger("app.py").error("Impossibile salvare immagine ".format(e))
        raise
    return ratio, size  # ratio e size serviranno anche dopo!


def parseXML(xml_foler, images_folder, final_images_folder):
    """
    Blocco logico principale per l'esecuzione. Parse xml, estrazione info, chiama la funzione per immagini e restituisce liste di oggetti

    Args:
        xml_foler: cartella xml input
        images_folder: cartella img input
        final_images_folder: cartella img output

    Raises:
        Exception: cartella xml vuota

    Returns:
        liste di oggetti immagini, categorie e annotazioni
    """

    catId = 0
    imageId = 0
    annId = 0

    categories = []
    images = []
    annoations = []

    cat_names = []

    files = [f for f in listdir(xml_foler) if isfile(join(xml_foler, f))]
    if len(files) <= 0:
        raise Exception("La cartella XML inserita non contiente file!")
    logging.getLogger("app.py").debug(
        "Trovti file xml da lavorare: {0}".format(len(files))
    )

    for file in files:
        tree = ET.parse(join(xml_foler, file))

        # Parse image data
        filename = tree.findall(".//filename")[0].text
        logging.getLogger("app.py").info("--Mi occupo del file: {0}".format(filename))
        imageId += 1
        width = tree.findall(".//width")[0].text
        height = tree.findall(".//height")[0].text
        curr_ratio, curr_size = check_resize_save_img(
            filename, width, height, images_folder, final_images_folder
        )
        # Create Image object
        img = Ima(imageId, curr_size[0], curr_size[1], filename)
        images.append(img)

        # Parsing categories and annotations info
        names = tree.findall(".//name")
        xmins = tree.findall(".//xmin")
        ymins = tree.findall(".//ymin")
        xmaxs = tree.findall(".//xmax")
        ymaxs = tree.findall(".//ymax")
        logging.getLogger("app.py").info(
            "---Trovate annotazioni: {0}".format(len(names))
        )

        for name, xmin, ymin, xmax, ymax in zip(names, xmins, ymins, xmaxs, ymaxs):
            # Dealing with categories
            if name.text in cat_names:
                # check if current category was already created
                for cat in categories:
                    if cat.get_name() == name.text:
                        curr_cat = cat.get_id()
                        break  # keep appropriate category id
            else:
                # if not, create new category
                catId += 1
                curr_cat = catId
                # create categry objct
                cat = Category(catId, name.text)
                categories.append(cat)
                # append name for future checks
                cat_names.append(name.text)

            # get the correct sizes of the box
            # (curr_ratio is a tuple with x and y resize ratios
            # (can also be (1,1) if image not changed))
            xmin = int(xmin.text) * curr_ratio[0]
            xmax = int(xmax.text) * curr_ratio[0]
            ymin = int(ymin.text) * curr_ratio[1]
            ymax = int(ymax.text) * curr_ratio[1]
            w = xmax - xmin
            h = ymax - ymin

            annId += 1
            # create Annotation objct
            ann = Annotation(annId, imageId, curr_cat, [xmin, ymin, w, h])
            annoations.append(ann)

    return images, categories, annoations


def get_dicts(images, cagetories, annotations):
    """
    Prese le liste di oggetti, crea dizionario unico

    Args:
        images: lista oggetti immagine
        cagetories: lista oggetti categoria
        annotations: lista oggetti annotazione

    Returns:
        dizionario finale unico da convertire in json
    """

    d = dict()
    logging.getLogger("app.py").debug("Costruisco dizionario")

    logging.getLogger("app.py").info("--Costruisco dizionario categorie")
    # categories dict
    dicts = []
    for c in cagetories:
        d1 = dict()
        d1["id"], d1["name"], d1["supercategory"] = c.get_data()
        dicts.append(d1)
    d["cagetories"] = dicts

    logging.getLogger("app.py").info("--Costruisco dizionario immagini")
    # images dict
    dicts = []
    for i in images:
        d1 = dict()
        d1["id"], d1["width"], d1["height"], d1["file_name"] = i.get_data()
        dicts.append(d1)
    d["images"] = dicts

    logging.getLogger("app.py").info("--Costruisco dizionario annotazioni")
    # annotations dict
    dicts = []
    for a in annotations:
        d1 = dict()
        d1["id"], d1["image_id"], d1["category_id"], d1["bbox"] = a.get_data()
        dicts.append(d1)
    d["annotations"] = dicts

    return d


logging.basicConfig()
logging.getLogger("app.py").setLevel(logging.DEBUG)
warnings.filterwarnings("ignore")

# Gestione argomenti in input
parser = argparse.ArgumentParser()
try:
    parser.add_argument("imagedir")
    parser.add_argument("xmldir")
    parser.add_argument("outputdir")
    args = parser.parse_args()
    images_folder = args.imagedir
    xml_foler = args.xmldir
    final_images_folder = args.outputdir
    logging.getLogger("app.py").info("Parametri inseriti:")
    logging.getLogger("app.py").info("- imagedir = {0}".format(images_folder))
    logging.getLogger("app.py").info("- imagedir = {0}".format(xml_foler))
    logging.getLogger("app.py").info("- imagedir = {0}".format(final_images_folder))
except Exception as e:
    logging.getLogger("app.py").error(
        "Errore inserimento parametri input: {0}".format(e)
    )


# Parsing xml e resizing immagini
images, categories, annotations = parseXML(
    xml_foler, images_folder, final_images_folder
)

# Trasformazione dati in un dizionario unico
data = get_dicts(images, categories, annotations)

# Stampa json finale
try:
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
except Exception as e:
    logging.getLogger("app.py").error(
        "Impossibile salvare il dizionario come file json: ".format(e)
    )

logging.getLogger("app.py").debug("Operazione completata")
