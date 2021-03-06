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
    statisticPointlist_och = ['opr', 'ltemp','lbc','fec-ber','cd', 'snr', 'cfo', 'dgd', 'osnr', 'snr-x', 'snr-y', 'cc-opr', 'fec-ber-x-corr', 'fec-ber-y-corr']
    statisticPointlist_otu = ['opr', 'ltemp', 'lbc', 'fec-ber', 'cd', 'snr', 'cfo', 'dgd', 'osnr', 'snr-x', 'snr-y', 'fec-ber-x-corr', 'fec-ber-y-corr']
    statisticPointlist = statisticPointlist_och
    # while(1):
    global host_id, transceiver_id,fre, txpower
    if (float(fre) == 1):
        if (host_id == '0'):
            host = '192.168.108.161'
        elif (host_id == '1'):
            host = '192.168.108.164'

        if (transceiver_id == '1'):
            interface1 = 'otu4:1/2/1/1'
            statisticPointlist = statisticPointlist_otu
        elif (transceiver_id == '2'):
            interface1 = 'och:1/1/2/1/1.1'
        elif (transceiver_id == '3'):
            interface1 = 'och:1/1/2/1/2.1'

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

            time1 = txpower
            time1 = str.rstrip(time1)

            doc = xml.dom.minidom.Document()
            root = doc.createElement('statistics')
            root.setAttribute('xmlns', "http://btisystems.com/ns/atlas")
            doc.appendChild(root)
            historical = doc.createElement('historical')
            root.appendChild(historical)
            entity = doc.createElement('entity')
            historical.appendChild(entity)
            entityname = doc.createElement('entityName')
            entity.appendChild(entityname)
            entityname.appendChild(doc.createTextNode(str(interface1)))
            binLength = doc.createElement('binLength')
            entity.appendChild(binLength)
            length = doc.createElement('length')
            length.appendChild(doc.createTextNode('1Minute'))
            binLength.appendChild(length)
            interval = doc.createElement('interval')
            binLength.appendChild(interval)

            binStart = doc.createElement('binStart')
            binStart.appendChild(doc.createTextNode(str(time1)))
            interval.appendChild(binStart)
            for i in range(len(statisticPointlist)):
                statisticList = doc.createElement('statisticList')
                statisticPoint = doc.createElement('statisticPoint')
                statisticList.appendChild(statisticPoint)
                statisticPoint.appendChild(doc.createTextNode(statisticPointlist[i]))
                interval.appendChild(statisticList)

            fp_xml = open('kjw300.xml', 'w+')
            doc.writexml(fp_xml)
            fp_xml.close()
            soup = BeautifulSoup(open('kjw300.xml'), 'xml')

            result = m.get(filter=('subtree', soup)).data_xml
            # logging.info(result)
            fp = open('kjw200.xml', 'w+')
            fp.write(result)
            fp.close()
            '''通过minidom解析xml文件'''
            xmlfilepath = os.path.abspath("kjw200.xml")
            tree = ET.parse(xmlfilepath)
            root = tree.getroot()
            valuelist=[]
            try:
                for i in range(len(statisticPointlist)):
                    value = root[0][0][0][1][1][i + 1][2].text
                    print(statisticPointlist[i] + ':' + value)
                    valuelist.append(value)
                fre = 0.0
                senddata = 'transceiver_id:'+ transceiver_id + ' ' + statisticPointlist[0] + ':' + valuelist[0] + ' '
                for i in range(1, len(valuelist)):
                    if(transceiver_id == '1' and (i == 11)):
                        senddata = senddata +'cc-opr'+ ':' + '-100' + ' '    #add cc-opr but donot use
                    else:
                        senddata = senddata + statisticPointlist[i] + ':' + valuelist[i] + ' '
                conn.sendall((senddata+'\n').encode())
            except Exception as e:
                print(e)
                conn.sendall(('wrong\n').encode())

def pushfre():  #(otu4:1/2/1/1) tx-power out of range for coherent CFP transceiver, valid range = -15.00 to +1.00 dBm

    global FLAG, modu, last_modu
    #otu4:1/2/1/1 port can not change modulation and config modulation
    while(FLAG):
        global conn, host_id, transceiver_id, fre, txpower;
        data1 = str(conn.recv(1024), encoding="utf-8")
        recv_data = data1.split()
       # print('recv_data', recv_data)
        if(recv_data == []): # disconnect
            FLAG = 0
        try:
            if(len(recv_data) == 5):
                host_id, transceiver_id, fre, txpower, modu_tmp= recv_data  #data format for config, when transceiver == 1, modu_temp = qpsk
                modu[int(host_id)][int(transceiver_id)] = str.rstrip(modu_tmp)
                print('host:', host_id, 'transceiver:', transceiver_id, 'fre:', fre, 'txpower:', txpower, 'modulation:', modu[int(host_id)][int(transceiver_id)])
                # modu = str.rstrip(modu)

            else:
                host_id, transceiver_id, fre, txpower = recv_data   # this is for data query, fre is 1 and txpower actually is time , when transceiver = 4, send all transceiver data
                print('host:', host_id, 'transceiver:', transceiver_id, 'fre:', fre, 'time:', txpower)
        except Exception as e:
            print('Exception:',e)
            #print('fre',fre)
            continue
        if(host_id == '0'):
            host = '192.168.108.161'
        elif (host_id == '1'):
            host = '192.168.108.164'

        if(transceiver_id == '1'):   #otu4 is not the same as och
            interface1 = 'otu4:1/2/1/1'
            Container = 'f:otnOtuContainer'
            type1 = 'otnOtu'
        elif(transceiver_id == '2'):
            interface1 = 'och:1/1/2/1/1.1'
            cross_connect_source = '10ge:1/1/1/3/1'
            cross_connect_dst = 'odu2e:1/1/2/1/1.1.1.9'
            otu4 = 'otu4:1/1/2/1/1.1.1'
            Container = 'f:ochIfContainer'
            type1 = 'opticalChannel'
        elif(transceiver_id == '3'):
            interface1 = 'och:1/1/2/1/2.1'
            cross_connect_source = '10ge:1/1/1/6/1'
            cross_connect_dst = 'odu2e:1/1/2/1/2.1.1.1'
            otu4 = 'otu4:1/1/2/1/2.1.1'
            Container = 'f:ochIfContainer'
            type1 = 'opticalChannel'

        if(float(fre) > 190):
            with manager.connect(host = host, port=2022, username="admin", password="admin",
                                     look_for_keys=False) as m:
                print('modu:',modu, 'last_modu',last_modu, 'host_id:', host_id, 'transceiver_id', transceiver_id)
                if (modu[int(host_id)][int(transceiver_id)] != last_modu[int(host_id)][int(transceiver_id)]): #process when change modulation

                    '''remove cross-connect'''
                    doc = xml.dom.minidom.Document()
                    root = doc.createElement('config')
                    doc.appendChild(root)
                    interfaces = doc.createElement('circuits')
                    interfaces.setAttribute('xmlns', "http://btisystems.com/ns/atlas-interfaces")
                    root.appendChild(interfaces)
                    interface = doc.createElement('circuit')
                    interface.setAttribute('operation', "remove")
                    interfaces.appendChild(interface)
                    srcname = doc.createElement('source-name')
                    srcname.appendChild(doc.createTextNode(str(cross_connect_source)))
                    interface.appendChild(srcname)
                    dstname = doc.createElement('destination-name')
                    dstname.appendChild(doc.createTextNode(str(cross_connect_dst)))
                    interface.appendChild(dstname)
                    fp_xml = open('kjw_test5.xml', 'w+')
                    doc.writexml(fp_xml)
                    fp_xml.close()
                    soup = BeautifulSoup(open('kjw_test5.xml'), 'xml')
                    result1 = m.edit_config(config=soup, target='running', default_operation='merge')
                    logging.info(result1)

                    '''remove interface when config different modulation'''
                    last_modu[int(host_id)][int(transceiver_id)] = modu[int(host_id)][int(transceiver_id)]
                    doc1 = xml.dom.minidom.Document()
                    root = doc1.createElement('config')
                    doc1.appendChild(root)
                    interfaces = doc1.createElement('interfaces')
                    interfaces.setAttribute('xmlns', "urn:ietf:params:xml:ns:yang:ietf-interfaces")
                    interfaces.setAttribute('xmlns:f', "http://btisystems.com/ns/atlas-interfaces")
                    root.appendChild(interfaces)
                    interface = doc1.createElement('interface')
                    interface.setAttribute('operation', "remove")
                    interfaces.appendChild(interface)
                    name = doc1.createElement('name')
                    name.appendChild(doc1.createTextNode(str(interface1)))
                    interface.appendChild(name)
                    fp_xml = open('kjw_test2.xml', 'w+')
                    doc1.writexml(fp_xml)
                    fp_xml.close()
                    soup = BeautifulSoup(open('kjw_test2.xml'), 'xml')
                    result1 = m.edit_config(config=soup, target='running', default_operation='merge')
                    logging.info(result1)

                '''enabled false, config fre, tx-power and modulation'''
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
                type = doc.createElement('type')
                type.appendChild(doc.createTextNode(str(type1)))
                interface.appendChild(type)
                otnOtuContainer = doc.createElement(str(Container))
                interface.appendChild(otnOtuContainer)
                frequency = doc.createElement('f:frequency')
                frequency.appendChild(doc.createTextNode(str(fre)))
                otnOtuContainer.appendChild(frequency)
                if (transceiver_id != '1'):
                    fectype = doc.createElement('f:fec-type')
                    fectype.appendChild(doc.createTextNode('sd-fec-25pc'))
                    otnOtuContainer.appendChild(fectype)
                txpower1 = doc.createElement('f:tx-power')
                txpower1.appendChild(doc.createTextNode(str(txpower)))
                otnOtuContainer.appendChild(txpower1)
                if(transceiver_id != '1'):
                    modulation = doc.createElement('f:modulation')
                    modulation.appendChild(doc.createTextNode((str(modu[int(host_id)][int(transceiver_id)]))))
                    otnOtuContainer.appendChild(modulation)
                    losmod = doc.createElement('f:extended-los-mode')
                    losmod.appendChild(doc.createTextNode('true'))
                    otnOtuContainer.appendChild(losmod)
                fp_xml = open('kjw4.xml', 'w+')
                doc.writexml(fp_xml)
                fp_xml.close()

                fre = 0  # change the fre

                ''' enabled true '''
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

                if (modu[int(host_id)][int(transceiver_id)] != last_modu[int(host_id)][int(transceiver_id)]): # process when change modulation
                    '''
                    config otu4 
                    '''
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
                    name.appendChild(doc.createTextNode(str(otu4)))
                    enabled = doc.createElement('enabled')
                    enabled.appendChild((doc.createTextNode('true')))
                    interface.appendChild(name)
                    interface.appendChild(enabled)
                    type = doc.createElement('type')
                    type.appendChild(doc.createTextNode('otnOtu'))
                    interface.appendChild(type)
                    fp_xml = open('kjw_test3.xml', 'w+')
                    doc.writexml(fp_xml)
                    fp_xml.close()

                    '''config cross connect '''
                    doc = xml.dom.minidom.Document()
                    root = doc.createElement('config')
                    doc.appendChild(root)
                    interfaces = doc.createElement('circuits')
                    interfaces.setAttribute('xmlns', "http://btisystems.com/ns/atlas-interfaces")
                    root.appendChild(interfaces)
                    interface = doc.createElement('circuit')
                    interfaces.appendChild(interface)
                    srcname = doc.createElement('source-name')
                    srcname.appendChild(doc.createTextNode(str(cross_connect_source)))
                    interface.appendChild(srcname)
                    dstname = doc.createElement('destination-name')
                    dstname.appendChild(doc.createTextNode(str(cross_connect_dst)))
                    interface.appendChild(dstname)
                    directionality = doc.createElement('directionality')
                    directionality.appendChild(doc.createTextNode('2way'))
                    interface.appendChild(directionality)
                    rate = doc.createElement('rate')
                    rate.appendChild(doc.createTextNode('odu2e'))
                    interface.appendChild(rate)
                    fp_xml = open('kjw_test4.xml', 'w+')
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

                if (modu[int(host_id)][int(transceiver_id)] != last_modu[int(host_id)][int(transceiver_id)]):

                    soup = BeautifulSoup(open('kjw_test3.xml'), 'xml')
                    print('soup', soup)
                    result1 = m.edit_config(config=soup, target='running', default_operation='merge')
                    logging.info(result1)

                    soup = BeautifulSoup(open('kjw_test4.xml'), 'xml')
                    print('soup', soup)
                    result1 = m.edit_config(config=soup, target='running', default_operation='merge')
                    logging.info(result1)
        elif(int(fre) == 1):
            if(transceiver_id != '4'):
                Getpower()
            else:
                for i in range(1,4):
                    transceiver_id = str(i)
                    fre = 1
                    print('i:', i, 'transceiver_id', transceiver_id)
                    Getpower()





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
    host_id = 10
    transceiver_id = 0
    fre = 0
    txpower = 0
    host_num = 2;
    port_num = 3;
    modu = [[None] * (port_num+1) for i in range((host_num+1))]
    last_modu = [[None] * (port_num+1) for i in range((host_num+1))]
    last_modu[0][1] = str('qpsk')
    last_modu[1][1] = str('qpsk')

    while 1:
        conn, addr = s.accept()
        FLAG = 1

        # conn = connection[-1]
        # addr = address[-1]

        print("socket connect success, address:", addr)


        '''two threads, one is used to collect power, one is used to configure the center frequency'''
        proc = threading.Thread(target=pushfre)
        proc.start()

        # proc1 = threading.Thread(target=Getpower)
        # proc1.start()




    # Getpower_pushfre(interface1='otu4:1/2/1/1',fre=193.4)
