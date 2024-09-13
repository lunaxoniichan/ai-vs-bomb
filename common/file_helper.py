import json


class FileHelper:
    @staticmethod
    def read_json(path):
        with open(path) as f:
            return json.load(f)

    @staticmethod
    def write_json(dictionary, path):
        json_object = json.dumps(dictionary, indent=4)
        with open(path, "w") as outfile:
            outfile.write(json_object)

    @staticmethod
    def read_txt(path, mode="r"):
        with open(path, mode) as f:
            return f.read()

    @staticmethod
    def write_txt(path, txt, mode="w"):
        with open(path, mode) as f:
            f.write(txt)
