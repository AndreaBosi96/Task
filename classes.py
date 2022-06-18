# Classe padre
class Data:
    def __init__(self, id):
        self.id = id

    def get_id(self):
        return self.id


# Classe per immagini
class Ima(Data):
    def __init__(self, id, width, height, file_name):
        self.id = id
        self.width = width
        self.height = height
        self.file_name = file_name

    def get_data(self):
        return self.id, self.width, self.height, self.file_name


# Classe per categorie
class Category(Data):
    def __init__(self, id, name):
        self.id = id
        self.name = name

        # Gestione super categoria: non avendo info e non trovandola sugli xml, l'ho scelta in maniera arbitraria
        if name in ["cat", "dog"]:
            self.supercategory = "animal"
        elif name == "person":
            self.supercategory = name
        else:
            self.supercategory = "object"

    def get_name(self):
        return self.name

    def get_data(self):
        return self.id, self.name, self.supercategory


# Classe per le annotazioni
class Annotation(Data):
    def __init__(self, id, image_id, category_id, bbox):
        self.id = id
        self.image_id = image_id
        self.category_id = category_id
        self.bbox = bbox

    def get_data(self):
        return self.id, self.image_id, self.category_id, self.bbox
