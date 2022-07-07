import urllib


class MetaDataCreator:
    """
    A method to encode data for the metadata field for the IMX api
    """

    def __init__(self):
        """
        The constructor for the MetaDataCreator class
        """
        pass

    @staticmethod
    def encode_meta_data_dic(meta_data_dic):
        """
        A method to encode meta data
        :param meta_data_dic: meta data in form of a dictionary
        :return: an encoded string
        """
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
        """
        A method to encode search by asset name
        :param asset_name: the asset name searched
        :return: the encoded asset name
        """
        metadata = """{"name":[\"""" + asset_name + "\"]}"
        metadata_enc = urllib.parse.quote(metadata)
        return metadata_enc

    @staticmethod
    def encode_stark_signature(stark_signature):
        """
        A method to encode a stark signature
        :param stark_signature: the signature to be encoded
        :return: the encoded stark signature
        """
        metadata = """'{"stark_signature": \"""" + stark_signature + "\"}'"
        print(metadata)
        metadata_enc = urllib.parse.quote(metadata)
        return metadata_enc
