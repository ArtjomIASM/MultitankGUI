# IP, PORT FOR CLIENT AND SERVER CONFIGURATION
# IP, PORT LENGTH CONFIGURATION

# TTU
"""
DEFAULT_CLIENT_PORT = "7071"
DEFAULT_CLIENT_IP = "192.168.11.118"
DEFAULT_SERVER_PORT = "7070"
DEFAULT_SERVER_IP = "192.168.11.101"
"""
# Home

DEFAULT_CLIENT_PORT = "3031"
DEFAULT_CLIENT_IP = "127.0.0.1"
DEFAULT_SERVER_PORT = "3030"
DEFAULT_SERVER_IP = "127.0.0.1"

IP_LEN = 15
PORT_LEN = 4

# END OF IP, PORT CONFIGURATION
# ==============================================================================

# DATA FRAMES RECEIVE E.G 1 / 0.5 = 2.0 SECONDS
MAX_FRAMES_PER_SEC_TO_RECEIVE = 2.0  # How often receiver receive data # was 30.0 # matlab 100 in sec (0.5)
# ==============================================================================

# PID CONFIGURATION
PID_SAMPLE_TIME = 0.5  # Parameter for PID controller "sample time"
# ==============================================================================

# Graph interval for delay in millisecond / Change it if you have weak cpu

TIMED_INTERVAL = 66
# ==============================================================================


# CSV DATA FORMAT
FMT_FLOAT = '{0:.4f}'

def formatFloat(val):
    strVal = FMT_FLOAT.format(val)
    nDotIdx = -1
    for pos, char in enumerate(strVal):
        if char == ".":
            nDotIdx = pos

    nAfterDot = 0
    if -1 != nDotIdx:
        nAfterDot = len(strVal) - nDotIdx - 1
    if 0 == nAfterDot:
        strVal += '.0000'
    else:
        strVal.rjust(4 - nAfterDot, '0')
    return strVal
# ==============================================================================