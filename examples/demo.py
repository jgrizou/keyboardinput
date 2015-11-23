from keyboardinput import KeyboardInput

keyinput = KeyboardInput()
keyinput.start()

while keyinput.is_alive():  # ctrl-c will kill this on linux, see DEFAULT_INTERRUPT_CODE
    ret = keyinput.read(1)  # read with timeout of 1 second
    if ret:
        # print what ever you type
        print '\r', ret  # '\r' to prin a the beginning of the line,  I don't know why but this all thing make the print function do weird stuff.
    else:
        print '\rNothing typed...'

keyinput.join()
