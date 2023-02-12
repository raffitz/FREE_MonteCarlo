'''Functions relating to experiment details'''


def msg_to_config_experiment(config_json):
    '''Get message with experiment configurations'''
    cmd = "cfg\t"+str(config_json["config"]["deltaX"])+"\t" + \
          str(config_json["config"]["samples"])+"\r"
    cmd = cmd.encode(encoding="ascii")
    return cmd


def data_to_json(pic_message):
    '''Convert experiment data to JSON'''
    return {"Sample_number": str(pic_message[0]),
            "Val1": str(pic_message[1]),
            "Val2": str(pic_message[2]),
            "Val3": str(pic_message[3]),
            "Val4": str(pic_message[4])}
