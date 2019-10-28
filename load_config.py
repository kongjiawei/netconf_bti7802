from ncclient import manager
from ncclient.xml_ import *
import os
import xml.dom.minidom as xmldom
import xml.etree.ElementTree as ET
import logging

doc = xmldom.Document

if __name__ == "__main__":
    LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)
    host = "192.168.108.161"
    with manager.connect(host="192.168.108.161", port=2022, username="admin", password="admin",look_for_keys=False) as m:


        stats_filter = """
                          <config>
                              <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces" xmlns:f="http://btisystems.com/ns/atlas-interfaces">  
                                 <interface>
                                    <name>otu4:1/2/1/1</name>
                                    <f:otnOtuContainer >  
                                        <f:frequency>193.1</f:frequency>
                                    </f:otnOtuContainer>
                                  </interface>
                              </interfaces>          
                          </config>
                      """
       # result1 = m.edit_config(source = 'running', filter=('subtree', stats_filter))
        result1 = m.edit_config( config = stats_filter, target = 'running', default_operation = 'merge' )
       # print(m.validate(source = 'candidate'))
        logging.info(result1)
     #   m.commit()
        fp = open('kjw.xml', 'w+')
  #      fp.write(result1)
        fp.close()
        print(result1)

    '''通过minidom解析xml文件'''
    '''
    xmlfilepath = os.path.abspath("kjw.xml")
    tree = ET.parse(xmlfilepath)
    root = tree.getroot()
    print(root)
    print(root[0][0][0][1][1][2].text)
     <name>cfp:1/2/1/1</name>
                                   <opticalAttributes>
                                      <is-tunable>false</is-tunable>
                                      <grid>50</grid>
                                      <wavelength>1552.52</wavelength>
                                      <type>cfp</type>
                                   </opticalAttributes>
                                   
                          <config>
                             <inventory xmlns="http://btisystems.com/ns/atlas">
                                <name>chassis:1</name>
                                <media>optical</media>
                                <transceiver>
                                   <name>cfp:1/2/1/1</name>
                                   <opticalAttributes>
                                      <wavelength>1552.52</wavelength>
                                   </opticalAttributes>
                                 </transceiver>
                             </inventory>                                
                          </config>
                           <config>
                             <inventory xmlns="http://btisystems.com/ns/atlas">
                                 <name>chassis:1</name>
                                 <transceiver>
                                    <name>cfp:1/2/1/1</name>
                                    <media>optical</media>  
                                    <opticalAttributes>
                                        <is-tunable>false</is-tunable>
                                        <grid>f50GHz</grid>
                                        <wavelength>1552.52</wavelength>
                                    </opticalAttributes>     
                                 </transceiver>              
                             </inventory>                                
                          </config>
                          
                          <equipment xmlns="http://btisystems.com/ns/atlas">
                                 <name>chassis:1</name>
                                 <module>
                                    <module-name>ufm:1/2</module-name>
                                    <bic>
                                        <bic-name>bic:1/2/1</bic-name>
                                        <bic-type>cfp-bic</bic-type>
                                        <transceiver>
                                            <name>cfp:1/2/1/1</name>
                                            <optical-format>tunableX1</optical-format>
                                            <admin-status>up</admin-status>
                                            <custom2>kjwkjw</custom2>
                                        </transceiver>
                                     </bic>                                    
                                  </module>
                             </equipment>  
    '''

