import json
import logging
import os

from root_path import root_dir


class ImmediateSetting(object):

	def __init__(self, default: object = 0):
		self.default = default


class DeferredSetting(object):

	def __init__(self, default: object = 0):
		self.default = default


class TransientSetting(object):

	def __init__(self, default: object = 0):
		self.default = default


class Config(dict):

	immediate = ("recent_ovls", )
	recent_ovls = ImmediateSetting([])
	current_ovl = TransientSetting("some_ovl.ovl")
	name = "config.json"

	def __setitem__(self, k, v):
		super().__setitem__(k, v)
		if k in self.immediate:
			logging.debug(f"Saved '{self.name}' after storing '{k}'")
			self.save()
	#
	# def __getitem__(self, k):
	# 	return self[k]

	def __init__(self, name="config.json", **kwargs):
		super().__init__(**kwargs)
		self.name = name

	@property
	def cfg_path(self):
		return os.path.join(root_dir, self.name)

	def save(self):
		logging.info(f"Saving config")
		with open(self.cfg_path, "w") as json_writer:
			json.dump(self.__slots__, json_writer, indent="\t", sort_keys=True)

	def load(self):
		try:
			with open(self.cfg_path, "r") as json_reader:
				self.update(json.load(json_reader))
		except FileNotFoundError:
			logging.debug(f"Config file missing at {self.cfg_path}")
		except json.decoder.JSONDecodeError as e:
			logging.error(f"Config file broken at {self.cfg_path}")
			logging.error(str(e))


def save_config(cfg_dict):
	logging.info(f"Saving config")
	with open(os.path.join(root_dir, "config.json"), "w") as json_writer:
		json.dump(cfg_dict, json_writer, indent="\t", sort_keys=True)


def load_config():
	try:
		cfg_path = os.path.join(root_dir, 'config.json')
		with open(cfg_path, "r") as json_reader:
			return json.load(json_reader)
	except FileNotFoundError:
		logging.debug(f"Config file missing at {cfg_path}")
		return {}
	except json.decoder.JSONDecodeError as e:
		logging.error(f"Config file broken at {cfg_path}")
		logging.error(str(e))
		return {}


def read_str_dict(cfg_path):
	config_dict = {}
	try:
		with open(cfg_path, 'r', encoding='utf-8') as cfg_file:
			for line in cfg_file:
				if not line.startswith("#") and "=" in line:
					(key, val) = line.strip().split("=")
					key = key.strip()
					val = val.strip()
					if val.startswith("["):
						# strip list format [' ... ']
						val = val[2:-2]
						config_dict[key] = [v.strip() for v in val.split("', '")]
					else:
						config_dict[key] = val
	except:
		print(f"{cfg_path} is missing or broken!")
	return config_dict


def write_str_dict(cfg_path, config_dict):
	stream = "\n".join([key + "=" + str(val) for key, val in config_dict.items()])
	with open(cfg_path, 'w', encoding='utf8') as cfg_file:
		cfg_file.write(stream)


def read_list(cfg_path):
	try:
		with open(cfg_path, 'r', encoding='utf-8') as cfg_file:
			return [line.strip() for line in cfg_file if line.strip() and not line.startswith("#")]
	except:
		print(f"{cfg_path} is missing or broken!")
		return []


if __name__ == '__main__':
	cfg = read_str_dict("config.ini")
	print(cfg)
