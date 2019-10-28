# from ncclient import manager
# from ncclient.xml_ import *
# import os
# import xml.dom.minidom as xmldom
# import xml.etree.ElementTree as ET
# import logging
#
# doc = xmldom.Document
#
# if __name__ == "__main__":
#     LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
#     logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)
#     with manager.connect(host="192.168.108.161", port=2022, username="admin", password="admin",look_for_keys=False) as m:
#
#         """ This will return all of the PM intervals for a 10ge: Entity """
#
#         stats_filter = """
#                           <statistics xmlns="http://btisystems.com/ns/atlas">
#
#                           </statistics>
#                       """
#        # result1 = m.get_config(source = 'running').data_xml
#         result2 = m.get(filter = ('subtree', stats_filter)).data_xml
#         logging.info(result2)
#      #   result1 = m.get(filter = ('subtree', stats_filter))
#         #logging.info(result1)
#       #  result = m.get(('subtree',stats_filter)).data_xml
#        # fp = open('kjw1.xml', 'w+')
#       #  fp.write(result1)
#       #  fp.close()
#       #  print(result1)
#         fp1 =  open('kjw2.xml','w+')
#         fp1.write(result2)
#         fp1.close()
#
#     '''通过minidom解析xml文件'''
#     # xmlfilepath = os.path.abspath("kjw.xml")
#     # tree = ET.parse(xmlfilepath)
#     # root = tree.getroot()
#     # print(root)
#     # print(root[0][0][0][1][1][2].text)
#


from ncclient import manager
from ncclient.xml_ import *
import os
import xml.etree.ElementTree as ET
import logging
import xml.dom.minidom
from bs4 import BeautifulSoup
from lxml import  etree
import socket
import threading
import time

def Getpower():
    while(1):
        global host_id, transceiver_id,fre
        if (host_id == '0'):
            host = '192.168.108.161'
        elif (host_id == '1'):
            host = '192.168.108.164'

        if (transceiver_id == '1'):
            interface1 = 'otu4:1/2/1/1'
        elif (transceiver_id == '2'):
            interface1 = 'och:1/1/2/1/1.1'
        elif (transceiver_id == '3'):
            interface1 = 'och:1/1/2/1/2.1'

        if (int(fre) == 1):
            with manager.connect(host=host, port=2022, username="admin", password="admin", look_for_keys=False) as m:

                stats_filter = """
                                  <statistics xmlns="http://btisystems.com/ns/atlas">
                                    <current>
                                       <entity>
                                            <entityName>interface</entityName>
                                            <binLength>
                                                <length>unTimed</length>
                                                <statisticList>
                                                    <statisticPoint>opr</statisticPoint>
                                                </statisticList>
                                            </binLength>
                                       </entity>                      		
                                    </current>
                                  </statistics>
                              """

                '''create get_power XML'''
                doc = xml.dom.minidom.Document()
                root = doc.createElement('statistics')
                root.setAttribute('xmlns', "http://btisystems.com/ns/atlas")
                doc.appendChild(root)
                current = doc.createElement('current')
                root.appendChild(current)
                entity = doc.createElement('entity')
                current.appendChild(entity)
                entityname = doc.createElement('entityName')
                entity.appendChild(entityname)
                entityname.appendChild(doc.createTextNode(str(interface1)))
                binLength = doc.createElement('binLength')
                entity.appendChild(binLength)
                length = doc.createElement('length')
                length.appendChild(doc.createTextNode('unTimed'))
                binLength.appendChild(length)
                statisticList = doc.createElement('statisticList')
                statisticPoint = doc.createElement('statisticPoint')
                statisticList.appendChild(statisticPoint)
                statisticPoint.appendChild(doc.createTextNode('opr'))
                binLength.appendChild(statisticList)

                fp_xml = open('kjw3.xml', 'w+')
                doc.writexml(fp_xml)
                fp_xml.close()
                soup = BeautifulSoup(open('kjw3.xml'),'xml')


                result = m.get(filter = ('subtree', soup)).data_xml
                logging.info(result)
                fp = open('kjw2.xml', 'w+')
                fp.write(result)
                fp.close()
                '''通过minidom解析xml文件'''
                xmlfilepath = os.path.abspath("kjw2.xml")
                tree = ET.parse(xmlfilepath)
                root = tree.getroot()
                power_value = root[0][0][0][1][1][2].text
                print('power_value', power_value)
                if(power_value < 10):
                    conn.send(power_value)
                    time.sleep(5)
def pushfre():

    while(1):
        global conn;
        data1 = str(conn.recv(1024), encoding="utf-8")
        print('data1:', data1, type(data1))
        host_id, transceiver_id, fre, null= data1.split(' ')
        print('host:', host_id, 'transceiver:', transceiver_id, 'fre:', fre)
        if(host_id == '0'):
            host = '192.168.108.161'
        elif (host_id == '1'):
            host = '192.168.108.164'

        if(transceiver_id == '1'):
            interface1 = 'otu4:1/2/1/1'
        elif(transceiver_id == '2'):
            interface1 = 'och:1/1/2/1/1.1'
        elif(transceiver_id == '3'):
            interface1 = 'och:1/1/2/1/2.1'

        if(float(fre) > 190):
            with manager.connect(host = host, port=2022, username="admin", password="admin",
                                     look_for_keys=False) as m:
                doc = xml.dom.minidom.Document()
                root = doc.createElement('config')
                doc.appendChild(root)
                interfaces = doc.createElement('interfaces')
                interfaces.setAttribute('xmlns', "urn:ietf:params:xml:ns:yang:ietf-interfaces")
                interfaces.setAttribute('xmlns:f', "http://btisystems.com/ns/atlas-interfaces")
                root.appendChild(interfaces)
                interface = doc.createElement('interface')
                interfaces.appendChild(interface)
                name = doc.createElement('name')
                name.appendChild(doc.createTextNode(str(interface1)))
                enabled = doc.createElement('enabled')
                enabled.appendChild((doc.createTextNode('false')))
                interface.appendChild(name)
                interface.appendChild(enabled)
                otnOtuContainer= doc.createElement('f:ochIfContainer')
                interface.appendChild(otnOtuContainer)
                frequency = doc.createElement('f:frequency')
                frequency.appendChild(doc.createTextNode(str(fre)))
                otnOtuContainer.appendChild(frequency)
                fp_xml = open('kjw4.xml', 'w+')
                doc.writexml(fp_xml)
                fp_xml.close()


                doc = xml.dom.minidom.Document()
                root = doc.createElement('config')
                doc.appendChild(root)
                interfaces = doc.createElement('interfaces')
                interfaces.setAttribute('xmlns', "urn:ietf:params:xml:ns:yang:ietf-interfaces")
                interfaces.setAttribute('xmlns:f', "http://btisystems.com/ns/atlas-interfaces")
                root.appendChild(interfaces)
                interface = doc.createElement('interface')
                interfaces.appendChild(interface)
                name = doc.createElement('name')
                name.appendChild(doc.createTextNode(str(interface1)))
                enabled = doc.createElement('enabled')
                enabled.appendChild((doc.createTextNode('true')))
                interface.appendChild(name)
                interface.appendChild(enabled)
                fp_xml = open('kjw5.xml', 'w+')
                doc.writexml(fp_xml)
                fp_xml.close()

                soup = BeautifulSoup(open('kjw4.xml'), 'xml')
                print('soup', soup)
                with open("kjw4.xml","r") as f:
                    data=f.readlines()
                print("data",data)
                result1 = m.edit_config(config=soup, target='running', default_operation='merge')
                logging.info(result1)

                soup = BeautifulSoup(open('kjw5.xml'), 'xml')
                print('soup', soup)
                result1 = m.edit_config(config=soup, target='running', default_operation='merge')
                logging.info(result1)


if __name__ == '__main__':
    # '''socket client'''
    # host = '192.168.108.25'
    # port = 8888
    # socket_lsq = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # socket_lsq.connect((host,port))
    # print('connect lsq success')
    LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)
    '''socket server'''
    host = '192.168.108.229'
    port = 9999
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    print('wait for connect')
    conn, addr = s.accept()
    print("socket connect success, address:", addr)

    '''two threads, one is used to collect power, one is used to configure the center frequency'''

    proc = threading.Thread(target= pushfre)
    proc.start()
    proc1 = threading.Thread(target=Getpower)
    #proc1.start()



    # Getpower_pushfre(interface1='otu4:1/2/1/1',fre=193.4)
