from sbp.client.drivers.pyserial_driver import PySerialDriver
from sbp.client import Handler, Framer
from sbp.navigation import SBP_MSG_BASELINE_NED, SBP_MSG_POS_LLH, \
    SBP_MSG_VEL_NED

import argparse
import pdb


class RtkMessage:
    '''
    Saves and outputs parsed RTK data from Piks
    '''

    def __init__(self):
        self.flag = 0.0
        self.n = 0.0
        self.e = 0.0
        self.d = 0.0
        self.lat = 0.0
        self.lon = 0.0
        self.h = 0.0
        self.v_n = 0.0
        self.v_e = 0.0
        self.v_d = 0.0


def read_rtk(port='/dev/ttyUSB0', baud=115200):
    '''
    Reads the RTK output from SwiftNav Piksi, parses the messege and prints.
    Piksi's must be configured to give RTK message through the serial port.
    NOTE: Current official sbp drivers only support python-2

    Args:
        port: serial port [[default='/dev/ttyUSB0']
        baud: baud rate [default=115200]

    Returns:
        None
    '''

    m = RtkMessage()

    # open a connection to Piksi
    with PySerialDriver(port, baud) as driver:
        with Handler(Framer(driver.read, None, verbose=True)) as source:
            try:
                msg_list = [SBP_MSG_BASELINE_NED, SBP_MSG_POS_LLH,
                            SBP_MSG_VEL_NED]
                for msg, metadata in source.filter(msg_list):

                    # LLH position in deg-deg-m
                    if msg.msg_type == 522:
                        m.lat = msg.lat
                        m.lon = msg.lon
                        m.h = msg.height

                    # RTK position in mm (from base to rover)
                    elif msg.msg_type == 524:
                        m.n = msg.n
                        m.e = msg.e
                        m.d = msg.d
                        m.flag = msg.flags

                    # RTK velocity in mm/s
                    elif msg.msg_type == 526:
                        m.v_n = msg.n
                        m.v_e = msg.e
                        m.v_d = msg.d

                    else:
                        pass

                    print "%.4f,%.4f,%.4f" % (m.n * 1e-3, m.e * 1e-3,
                                             m.d * 1e-3)

            except KeyboardInterrupt:
                pass

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            'Opens and reads the output of SwiftNav Piksi. \
            Developed based on Swift Navigation SBP example.'))
    parser.add_argument(
        '-p', '--port',
        default=['/dev/ttyUSB0'],
        nargs=1,
        help='specify the serial port to use [default = \'/dev/ttyUSB0\']')
    parser.add_argument(
        '-b', '--baud',
        default=[115200],
        nargs=1,
        help='specify the baud rate [default = 115200]')
    args = parser.parse_args()

    read_rtk(args.port[0], args.baud[0])
