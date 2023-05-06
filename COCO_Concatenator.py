
import json
from dataclasses import dataclass, asdict

@dataclass
class Annotation:
	id: int # esto se procesa externamente
	iscrowd: int
	image_id: int # esto se procesa externamente
	category_id: int # TODO: como hacer con esto?
	segmentation: [[float]]
	bbox: [float]
	area: float

@dataclass
class Image:
	id: int # eso se procesa externamente
	width: int
	height: int
	file_name: str

@dataclass
class Category:
	id: int
	name: str


class COCO_Concatenator:
	def __init__(self):
		self.image_id = 0
		self.annotation_id = 0
		self.categories_count = 0
		self.images = []
		self.annotations = []
		self.categories = []


	def read_file(self, file_name):
		content = None
		with open(file_name, 'r') as f:
			content = json.load(f)

		# TODO: que hacemos con las categorías?
		# vamos a leerlas de antemano y por cada nueva darle un id nuevo
		# no se va a comprobar colisiones de nombres ni nada
		# si dos categorias tienen el mismo nombre nos jodemos

		for categorie in content['categories']:
			(_, name) = categorie.values()
			self.categories_count += 1
			self.categories.append(Category(self.categories_count, name))

		for image in content['images']:
			(image_id, width, height, file_name) = image.values()
			self.image_id += 1
			self.images.append(Image(self.image_id, width, height, file_name))

			for ann in content['annotations']:
				(_, iscrowd, image_ref, _, segmentation, bbox, area) = ann.values()
				if image_id == image_ref:
					# TODO: por ahora cada archivo entrante es una categoria
					# por separado, pero habria que hacer para categorias iguales
					# con archivos separados
					self.annotations.append(Annotation(self.annotation_id,\
					iscrowd, self.image_id, self.categories_count, segmentation,\
					bbox, area))
					self.annotation_id += 1



	def join_to_file(self, file_name):
		data = {}
		data['info'] = { "description": "herramientras" }
		# print(data)
		data['images'] = [asdict(v) for v in self.images]
		# print(data)
		data['annotations'] = [asdict(v) for v in self.annotations]
		# print(data)
		data['categories'] = [asdict(v) for v in self.categories]
		# print(data)

		with open(file_name, 'w') as f:
			f.write(json.dumps(data))


	def read_multiple(self, file_names):
		for file_name in file_names:
			try:
				print("{file_name} readed")
				self.read_file(file_name)
			except OSError as err:
				print(err)




if __name__ == "__main__":

	import os
	from os import path
	import argparse

	parser = argparse.ArgumentParser(
		prog = "COCO Concatenator files",
		description = "Script to Concatenate COCO Files in One"
	)

	parser.add_argument('-f', '-filenames', dest="input_files", required=True, type=str, nargs='+', help='File(s) to be parsed and included in the output.')
	parser.add_argument('-o', '-output', dest="output_file", required=True, type=str, nargs=1, help='Output filename.')

	args = parser.parse_args()

	try:
		coco = COCO_Concatenator()
		coco.read_multiple(args.input_files)
		coco.join_to_file(args.output_file)
	except Exception as err:
		print(err)


