# https://blog.naver.com/chandong83/221156763486
from past.builtins import raw_input
import host
import sys

# Main  Routine
def main(portname):
    """
    Starts the Master RS-232 service
    """

    cmd_table = '''
    H or ? to show Help
    Q or CTRL+C to Quit
    V - Enable Verbose mode
    '''

    print("Starting RS-232 Master on port {:s}".format(portname))
    master = host.Host()
    master.start(portname)

    # Loop until we are to exit
    try:
        print(cmd_table)
        while master.running:

            cmd = raw_input()
            result = master.parse_cmd(cmd)
            if result is 0:
                pass
            elif result is 1:
                master.stop()
            elif result is 2:
                print(cmd_table)

    except KeyboardInterrupt:
        master.running = False

    print('\n\nGoodbye!')
    print('Port {:s} closed'.format(portname))


if __name__ == "__main__":
    main(sys.argv[1])