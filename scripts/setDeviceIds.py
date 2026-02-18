#! /usr/bin/env ccs-script
import argparse

from java.util import Properties
import java.io.FileOutputStream
import java.io.FileInputStream
import java.io.FileNotFoundException

def main(filename='test.properties'):

    properties_dict = {'BK9130B1/devName' : 'ASRL13::INSTR',
                       'BK9130B2/devName' : 'ASRL11::INSTR',
                       'BK1697/devName' : 'ASRL10::INSTR'}
    properties = Properties()

    try:
        input_stream = java.io.FileInputStream(filename)
        properties.load(input_stream)
        input_stream.close()
    except java.io.FileNotFoundException:
        pass

    for key, value in properties_dict.items():
        properties.setProperty(str(key), str(value))

    output_stream = java.io.FileOutputStream('test.properties')
    properties.store(output_stream, None)
    output_stream.close()

if __name__ == '__main__':

    main()
