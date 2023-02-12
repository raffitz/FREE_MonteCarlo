'''Send experiment data to e-lab-FREE server'''

import json
import importlib
import threading
import time
import configparser

import requests


# pylint: disable=too-many-instance-attributes
class ServerConnecion():
    '''Handle a connection to the server with all its configurations'''
    def __init__(self, ini_file):
        self.lock = threading.Lock()

        self.config_info = configparser.ConfigParser()
        self.config_info.read(ini_file)

        self.exp_config = []
        self.next_execution = {}
        self.status_config = {}
        self.save_data = []

        self.test = False
        self.test_end_point_print = True
        self.working = False
        self.waiting_for_config = True

        self.interface = None

        self.headers = {
          "Authentication": str(self.config_info['DEFAULT']['SECRET']),
          "Content-Type": "application/json"
        }

        self.api_protocol = 'http'
        if self.config_info['DEFAULT']['HTTPS']:
            self.api_protocol = 'https'

        self.timeout = 30

    def send_info_about_execution(self, execution_id):
        '''Send information about execution to e-lab-FREE server'''
        api_url = self.api_protocol+"://" + \
            self.config_info['DEFAULT']['SERVER']+":" + \
            self.config_info['DEFAULT']['PORT']+"/api/v1/execution/" + \
            str(execution_id)+"/status"
        # msg = {"secret":SEGREDO}
        print(api_url)
        response = requests.patch(api_url, headers=self.headers,
                                  json={"status": "R"},
                                  verify=False, timeout=self.timeout)
        print(response)
        return ''

    def send_exp_data(self):
        '''Send experiment data to e-lab-FREE server'''
        while self.interface.receive_data_from_exp() != "DATA_START":
            pass
        # send_message = {"value":"","result_type":"p"}#,
        #                 "status":"Experiment Starting"}
        # send_partial_result(send_message)
        while True:
            exp_data = self.interface.receive_data_from_exp()
            if self.config_info['DEFAULT']['DEBUG'] == "on":
                print("What pic send on serial port (converted to json): ",
                      json.dumps(exp_data, indent=4))
            try:
                exp_data = json.loads(exp_data)
            except json.JSONDecodeError:
                pass
            if exp_data != "DATA_END":
                self.save_data.append(exp_data)
                send_message = {"execution": int(self.next_execution["id"]),
                                "value": exp_data,
                                "result_type": "p"}  # ,"status":"running"}
                self.send_partial_result(send_message)
            else:
                send_message = {"execution": int(self.next_execution["id"]),
                                "value": self.save_data,
                                "result_type": "f"}
                self.send_partial_result(send_message)
                self.working = False
                self.next_execution = {}
                self.save_data = []
                time.sleep(0.00001)
                return

    def send_config_to_pic(self, myjson):
        '''Send configuration data to PIC'''
        print("Recebi mensagem de configure start. A tentar configurar pic")
        _, config_feita_correcta = self.interface.do_config(myjson)
        # se config feita igual a pedida? (opcional?)
        if config_feita_correcta:
            print(myjson["id"])
            self.send_info_about_execution(myjson["id"])
            data_thread = threading.Thread(target=self.send_exp_data,
                                           daemon=True)
            print("PIC configurado.\n")
            if self.interface.do_start():  # tentar começar experiencia
                self.working = True
                data_thread.start()
                time.sleep(0.000001)
                # O JSON dos config parameters está mal e crasha o server
                # (ARRANJAR)
                # send_mensage = '{"reply_id": "2",
                #                  "status": "Experiment Running",
                #                  "config_params":
                #                      "'+str(myjson["config_params"])+'"}'
                # self.working = True
                send_mensage = {"reply_id": "2",
                                "status": "Experiment Running"}
            else:
                send_mensage = {"reply_id": "2", "error": "-1",
                                "status": "Experiment could not start"}
        else:
            send_mensage = {"reply_id": "2", "error": "-2",
                            "status": "Experiment could not be configured"}
        return send_mensage

    # REST
    def get_config(self):
        '''Get apparatus configurations'''
        api_url = self.api_protocol+"://" + \
            self.config_info['DEFAULT']['SERVER']+":" + \
            self.config_info['DEFAULT']['PORT']+"/api/v1/apparatus/" + \
            self.config_info['DEFAULT']['APPARATUS_ID']
        # msg = {"secret":SEGREDO}
        print(api_url)
        response = requests.get(api_url, headers=self.headers, verify=False,
                                timeout=self.timeout)
        # print(response.json())
        self.exp_config = response.json()
        if self.config_info['DEFAULT']['DEBUG'] == "on":
            print(json.dumps(self.exp_config, indent=4))
        return ''

    def get_execution(self):
        '''Get apparatus execution'''
        api_url = self.api_protocol+"://" + \
            self.config_info['DEFAULT']['SERVER']+":" + \
            self.config_info['DEFAULT']['PORT']+"/api/v1/apparatus/" + \
            self.config_info['DEFAULT']['APPARATUS_ID']+"/nextexecution"
        response = requests.get(api_url, headers=self.headers, verify=False,
                                timeout=self.timeout)
        if response.json()['protocol']['config'] is not None:
            print(response.json())
            self.next_execution = response.json()
        if self.config_info['DEFAULT']['DEBUG'] == "on":
            print("REQUEST\n")
            print(json.dumps(self.next_execution, indent=4))
        return ''

    def send_partial_result(self, msg):
        '''Send partial results to e-lab-FREE server'''
        api_url = self.api_protocol+"://" + \
            self.config_info['DEFAULT']['SERVER']+":" + \
            self.config_info['DEFAULT']['PORT']+"/api/v1/result"
        if self.config_info['DEFAULT']['DEBUG'] == "on":
            print(str(msg))
            print(api_url)
            print("Aqui:  ", json.dumps(msg, indent=4))

        requests.post(api_url, headers=self.headers, json=msg, verify=False,
                      timeout=self.timeout)
        # Result_id = response.json()
        # if config_info['DEFAULT']['DEBUG'] == "on":
        #     print(json.dumps(Result_id,indent=4))
        return ''

    # if __name__ == "__main__":
    #     get_config()
    #     get_execution()
    #     print(json.dumps(next_execution,indent=4))
    #     send_partial_result()

    def main_cycle(self):
        '''Main execution cycle'''
        if self.exp_config is not None:
            if self.config_info['DEFAULT']['DEBUG'] == "on":
                print("Esta a passar pelo if none este\n")
            while True:
                if not self.working:
                    if self.config_info['DEFAULT']['DEBUG'] == "on":
                        print("Esta a passar pelo if none\n")
                    self.get_execution()
                    if self.test:
                        print("\n\nIsto_1 :")
                        print(self.next_execution)
                time.sleep(0.5)
                if ("config" in self.next_execution.keys()) and \
                        (not self.working) and \
                        self.next_execution["config"] is not None:
                    save_execution = self.next_execution.get("config", None)
                    if save_execution is not None:
                        print(json.dumps(save_execution))
                    # Estava a passar em cima e não sei bem pq:
                    # if save_execution != None:
                        self.status_config = \
                            self.send_config_to_pic(self.next_execution)
                    if self.test:
                        print("O valor do WORKING é: "+str(self.working))
                # pass
                # print("teste 12")
                # print(WORKING)

        return ''

    def run(self):
        '''Run client, collecting data from experiment and sending it to
        e-lab-FREE server'''
        print("[Starting] Experiment Client Starting...")
        # global next_execution
        self.interface = importlib.import_module("pic_interface.INTERFACE")\
            .MonteCarlo()
        while True:
            try:
                self.get_config()
                print("all good")
                if self.interface.do_init(self.exp_config["config"]):
                    print("Experiment " +
                          self.exp_config["config"]['id']+" Online !!")
                    self.main_cycle()
                else:
                    print("Experiment not found")
            except requests.exceptions.RequestException:
                # LOG ERROR
                print("Fail to connect to Server. Trying again after 10 s")
                # So faz shutdown do socket se este chegou a estar connected
                time.sleep(10)


if __name__ == "__main__":
    conn = ServerConnecion('server_info.ini')
    conn.run()


# global self.exp_config
# global INTERFACE
# INTERFACE = importlib.import_module("pic_interface.INTERFACE")
# print("Recebi mensagem de configuracao. "
#       "A tentar inicializar a experiencia\n")
# self.exp_config = myjson['config_file']

# # LIGAR A DISPOSITIVO EXP - INIT
# # Talvez passar erros em forma de string JSON para incluir no reply em vez
# # de OK e NOT OK
# if INTERFACE.do_init(self.exp_config) :
#     send('{"reply_id": "1", "status":"Experiment initialized OK"}')

# else :
#     send('{"reply_id": "1", "error":"-1", '
#          '"status":"Experiment initialized NOT OK"}')
