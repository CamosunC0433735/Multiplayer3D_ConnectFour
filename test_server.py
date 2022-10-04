import pytest
import subprocess
import time

#
# DO NOT CHANGE THE CODE BELOW
#

ERROR = b'E\n'
OK = b'O\n'

def stop_container():
    cmd = subprocess.run(['sudo', 'docker', 'stop', '226-server'], capture_output=True)
    print(cmd)
    cmd = subprocess.run(['sudo', 'docker', 'rm', '226-server'], capture_output=True)
    print(cmd)

def setup_module(module):
    stop_container()
    cmd = subprocess.run(['sudo', 'docker', 'build', '-t', '226-server', '.'], capture_output=True)
    print(cmd)
    cmd = subprocess.run(['sudo', 'docker', 'run', '-d', '--rm', '--name', '226-server', '-p', '12345:12345', '226-server'], capture_output=True)
    print(cmd)
    time.sleep(5) # Ugly; should properly detect when the container is up and running
    print('\n\n')

def teardown_module(module):
    print('\n\n')
    stop_container()
    print('\n\n')

def transmit(message):
    print('----\n')
    input = subprocess.Popen(['echo', message], stdout=subprocess.PIPE)
    print('>', input.args)
    output= subprocess.check_output(['nc', '127.0.0.1', '12345'], stdin=input.stdout)
    print('<', output)
    return output

#
# DO NOT CHANGE THE CODE ABOVE
#

def test_invalid_command():
    output = transmit('Test')
    assert output == ERROR

def test_get_board_command():
    output = transmit('G')
    assert output == b'____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n\n'

def test_put_and_clear_commands():
    output = transmit('P1231')
    assert output == OK
    output = transmit('G')
    assert output == b'____\n____\n____\n____\n\n____\n____\n___1\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n\n'
    output = transmit('C')
    assert output == OK
    output = transmit('G')
    assert output == b'____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n\n'

def test_out_of_sequence_put():
    output = transmit('P1231')
    assert output == OK
    output = transmit('P2102')
    assert output == OK
    output = transmit('P3023')
    assert output == OK
    output = transmit('P0311')
    assert output == OK
    output = transmit('P1221')
    assert output == ERROR
    output = transmit('G')
    assert output == b'____\n____\n____\n_1__\n\n____\n____\n___1\n____\n\n____\n2___\n____\n____\n\n__3_\n____\n____\n____\n\n\n'
    output = transmit('C')
    assert output == OK
    output = transmit('G')
    assert output == b'____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n\n'

def test_invalid_layer():
    output = transmit('P4231')
    assert output == ERROR
    output = transmit('G')
    assert output == b'____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n\n'
    output = transmit('C')
    assert output == OK

def test_invalid_row():
    output = transmit('P1431')
    assert output == ERROR
    output = transmit('G')
    assert output == b'____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n\n'
    output = transmit('C')
    assert output == OK

def test_invalid_column():
    output = transmit('P1241')
    assert output == ERROR
    output = transmit('G')
    assert output == b'____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n\n'
    output = transmit('C')
    assert output == OK

def test_invalid_token():
    output = transmit('P1234')
    assert output == ERROR
    output = transmit('G')
    assert output == b'____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n\n'
    output = transmit('C')
    assert output == OK

def test_invalid_put():
    output = transmit('PABCD')
    assert output == ERROR
    output = transmit('G')
    assert output == b'____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n____\n____\n____\n____\n\n\n'
    output = transmit('C')
    assert output == OK
