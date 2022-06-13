import urllib


class Metadata_Creator():

    def __init__(self):
        None

    @staticmethod
    def encode_meta_data_dic(meta_data_dic):
        start_str = "{"
        combination_str = start_str

        addition_counter = 0
        for key, value in meta_data_dic.items():
            addition_str = '"' + str(key) + """":[\"""" + str(value) + "\"]"
            combination_str = combination_str + addition_str

            if addition_counter == 0 and len(meta_data_dic) > 1:
                combination_str = combination_str + ','
            addition_counter = addition_counter + 1

        combination_str = combination_str + "}"

        encoded_str = urllib.parse.quote(combination_str)

        return encoded_str


    @staticmethod
    def encode_name_search(asset_name):
        metadata = """{"name":[\"""" + asset_name + "\"]}"
        metadata_enc = urllib.parse.quote(metadata)
        return metadata_enc

    @staticmethod
    def encode_stark_signature(stark_signature):
        metadata = """'{"stark_signature": \"""" + stark_signature + "\"}'"
        print(metadata)
        metadata_enc = urllib.parse.quote(metadata)
        return metadata_enc
