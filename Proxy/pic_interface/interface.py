#!/usr/bin/python3

'''Monte Carlo generator'''

from time import sleep
import json
import re
import random
import math


class MonteCarlo():
    '''Monte Carlo interface'''
    def __init__(self):
        self.serial_port = None
        self.size = None
        self.n_points = None
        self.frist = 1
        self.i = 1
        self.total_in = 0
        # status, config

    def print_serial(self):
        '''Print serial output'''
        while True:
            pic_message = self.serial_port.read_until(b'\r')
            pic_message = pic_message.decode(encoding='ascii')
            # Apanha os casos em que o pic manda /n/r
            if len(pic_message.strip()) > 1:
                print(pic_message.strip())

    def receive_data_from_exp(self):
        '''Receive experiment data'''
        if self.frist == 1:
            self.frist = 0
            return "DATA_START"
        if int(self.i) > int(self.n_points):
            sleep(0.01)
            print(f"Pi: {self.total_in * 1.0 / self.n_points * 1.0}")
            return "DATA_END"
        sleep(0.01)

        x_coord = random.uniform(-1.0, 1.0)*float(self.size)
        y_coord = random.uniform(-1.0, 1.0)*float(self.size)
        if math.sqrt(x_coord*x_coord+y_coord*y_coord) <= int(self.size):
            c_in = 1
            self.total_in = self.total_in + 1
        else:
            c_in = 0
        pic_message = '{"Sample_number":"'+str(self.i) + \
                      '","eX":"'+str(x_coord)+'","eY":"'+str(y_coord) + \
                      '","circ":"'+str(c_in)+'"}'
        # print (self.i)
        self.i = self.i + 1
        return pic_message

    # ALGURES AQUI HA BUG QUANDO NAO ESTA EM NENHUMA DAS PORTAS
    def try_to_lock_experiment(self, config_json):
        '''Try to lock experiment'''
        # LOG_INFO
        print("AH PROCURA DO PIC NA PORTA SERIE")
        pic_message = self.serial_port.read_until(b'\r')
        pic_message = pic_message.decode(encoding='ascii')
        pic_message = pic_message.strip()
        print("MENSAGEM DO PIC:\n")
        print(pic_message)
        print("\\-------- --------/\n")
        match = re.search(r"^(IDS)\s(?P<exp_name>[^ \t]+)"
                          r"\s(?P<exp_state>[^ \t]+)$", pic_message)
        if match.group("exp_name") == config_json['id']:
            # LOG_INFO
            print("ENCONTREI O PIC QUE QUERIA NA PORTA SERIE")
            if match.group("exp_state") == "STOPED":
                return True
            if self.do_stop():
                return True
            return False
        # LOG INFO
        print("NAO ENCONTREI O PIC QUE QUERIA NA PORTA SERIE")
        return False

    # DO_INIT - Abre a ligacao com a porta serie
    # NOTAS: possivelmente os returns devem ser jsons com mensagens de erro
    # melhores, por exemplo, as portas não existem ou não está o pic em nenhuma
    # delas outra hipotese é retornar ao cliente exito ou falha
    # e escrever detalhes no log do sistema
    def do_init(self, config_json):
        '''Initialize Monte Carlo generator'''
        if config_json['id'] == "DEV_TOOL":
            print("Isto é uma função de teste!\n")
            return True
        # LOG_ERROR - Serial port not configured on json.
        # return -2
        print("Falta serial config!\n")
        return False

    def do_config(self, config_json):
        '''Configure generator'''
        print(config_json)
        self.size = config_json["config"]["R"]
        self.n_points = config_json["config"]["Iteration"]

        print("Size :")
        print(self.size)
        print("\n")
        print("Numbero de pontos :")
        print(self.n_points)

        return config_json, True

    def do_start(self):
        '''Start generator'''
        self.total_in = 0
        self.i = 1
        self.frist = 1

        return True

    def do_stop(self):
        '''Stop generator'''
        print("A tentar parar experiencia\n")
        cmd = "stp\r"
        cmd = cmd.encode(encoding='ascii')
        self.serial_port.reset_input_buffer()
        self.serial_port.write(cmd)
        while True:
            pic_message = self.serial_port.read_until(b'\r')
            print("MENSAGEM DO PIC A CONFIRMAR STPOK:\n")
            print(pic_message.decode(encoding='ascii'))
            print("\\-------- --------/\n")
            if "STPOK" in pic_message.decode(encoding='ascii'):
                return True
            if re.search(r"(CONFIGURED|RESETED){1}$",
                         pic_message.decode(encoding='ascii')) is not None:
                return False
            # Aqui não pode ter else: false senão rebenta por tudo e por nada
            # tem de se apontar aos casos especificos -_-

    def do_reset(self):
        '''Reset generator'''
        print("A tentar fazer reset da experiencia\n")
        cmd = "rst\r"
        cmd = cmd.encode(encoding='ascii')
        self.serial_port.reset_input_buffer()
        self.serial_port.write(cmd)
        while True:
            pic_message = self.serial_port.read_until(b'\r')
            print("MENSAGEM DO PIC A CONFIRMAR RSTOK:\n")
            print(pic_message.decode(encoding='ascii'))
            print("\\-------- --------/\n")
            if "RSTOK" in pic_message.decode(encoding='ascii'):
                return True
            if re.search(r"(STOPED|CONFIGURED){1}$",
                         pic_message.decode(encoding='ascii')) is not None:
                return False
            # Aqui não pode ter else: false senão rebenta por tudo e por nada
            # tem de se apontar aos casos especificos -_-

    # get_status placeholder
    def get_status(self):
        '''Get generator status'''
        print("Esta funcao ainda nao faz nada\n")
        return True


if __name__ == "__main__":
    import sys
    import threading

    with open("./exp_config.json", "r", encoding='utf8') as fp:
        experiment_config_json = json.load(fp)
        # experiment_config_json = json.loads('{}')

        experiment = MonteCarlo()
        if not experiment.do_init(experiment_config_json):
            sys.exit("Não deu para abrir a porta. F")
        printer_thread = threading.Thread(target=experiment.print_serial)
        printer_thread.start()
        while True:
            experimen_cmd = input()+"\r"
            experimen_cmd = experimen_cmd.encode(encoding='ascii')
            experiment.serial_port.write(experimen_cmd)
