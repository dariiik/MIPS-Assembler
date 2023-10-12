import sys
import os
from enum import Enum
from tempfile import TemporaryFile
import re
import ctypes

################################################
# For debug option. 
# If you want to debug, set 1, program will show you some informations
# If not, set 0.
################################################
DEBUG = 1

MAX_SYMBOL_TABLE_SIZE = 1024
MEM_TEXT_START = 0x00400000
MEM_DATA_START = 0x10000000
BYTES_PER_WORD = 4
INST_LIST_LEN = 20


################################################
# Additional Components
################################################

class bcolors:
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    ENDC = '\033[0m'


start = '[' + bcolors.BLUE + 'START' + bcolors.ENDC + ']  '
done = '[' + bcolors.YELLOW + 'DONE' + bcolors.ENDC + ']   '
success = '[' + bcolors.GREEN + 'SUCCESS' + bcolors.ENDC + ']'
error = '[' + bcolors.RED + 'ERROR' + bcolors.ENDC + ']  '

pType = [start, done, success, error]


def log(printType, content):
    print(pType[printType] + content)


################################################
# Structure Declaration
################################################

class inst_t:
    def __init__(self, name, op, type, funct):
        self.name = name
        self.op = op
        self.type = type
        self.funct = funct


class symbol_t:
    def __init__(self):
        self.name = 0
        self.address = 0


class section(Enum):
    DATA = 0
    TEXT = 1
    MAX_SIZE = 2


################################################
# Global Variable Declaration
################################################

ADDIU = inst_t("addiu", "001001", "I", "")
ADDU = inst_t("addu",    "000000", 'R', "100001")
AND = inst_t("and",     "000000", 'R', "100100")
ANDI = inst_t("andi",    "001100", 'I', "")
BEQ = inst_t("beq",     "000100", 'I', "")
BNE = inst_t("bne",     "000101", 'I', "")
J = inst_t("j",       "000010", 'J', "")
JAL = inst_t("jal",     "000011", 'J', "")
JR = inst_t("jr",      "000000", 'R', "001000")
LUI = inst_t("lui",     "001111", 'I', "")
LW = inst_t("lw",      "100011", 'I', "")
NOR = inst_t("nor",     "000000", 'R', "100111")
OR = inst_t("or",      "000000", 'R', "100101")
ORI = inst_t("ori",     "001101", 'I', "")
SLTIU = inst_t("sltiu",    "001011", 'I', "")
SLTU = inst_t("sltu",    "000000", 'R', "101011")
SLL = inst_t("sll",     "000000", 'R', "000000")
SRL = inst_t("srl",     "000000", 'R', "000010")
SW = inst_t("sw",      "101011", 'I', "")
SUBU = inst_t("subu",    "000000", 'R', "100011")

inst_list = [ADDIU, ADDU, AND, ANDI, BEQ, BNE, J, JAL, JR,
             LUI, LW, NOR, OR, ORI, SLTIU, SLTU, SLL, SRL, SW, SUBU]

# Global Symbol Table
symbol_struct = symbol_t()
SYMBOL_TABLE = [symbol_struct] * MAX_SYMBOL_TABLE_SIZE

# For indexing of symbol table
symbol_table_cur_index = 0

# Temporary file stream pointers
data_seg = None
text_seg = None

# Size of each section
data_section_size = 0
text_section_size = 0


################################################
# Function Declaration - NO NEED TO CHANGE
################################################

# Change file extension form ".s" to ".o"
def change_file_ext(fin_name):
    fname_list = fin_name.split('.')
    fname_list[-1] = 'o'
    fout_name = ('.').join(fname_list)
    return fout_name


# Add symbol to global symbol table
def symbol_table_add_entry(symbol):
    global SYMBOL_TABLE
    global symbol_table_cur_index

    SYMBOL_TABLE[symbol_table_cur_index] = symbol
    symbol_table_cur_index += 1
    if DEBUG:
        log(1, f"{symbol.name}: 0x" + hex(symbol.address)[2:].zfill(8))


# Convert integer number to binary string
def num_to_bits(num, len):
    bit = bin(num & (2**len-1))[2:].zfill(len)
    return bit

def hex_to_num(hex):
    hex = str(hex)
    n = len(hex)
    m = 1
    num = 0
    for i in range(2, n):
        j = n + 1 - i
        if hex[j] == 'a':
            temp = 10
        elif hex[j] == 'b':
            temp = 11
        elif hex[j] == 'c':
            temp = 12
        elif hex[j] == 'd':
            temp = 13
        elif hex[j] == 'e':
            temp = 14
        elif hex[j] == 'f':
            temp = 15
        else:
            temp = int(hex[j]) 
        num += temp * m
        m *= 16
    return num

################################################
# Function Declaration - FILL THE BLANK AREA
################################################

# Fill the blanks
def make_symbol_table(input):
    size_bit = 0
    address = 0
    cur_section = section.MAX_SIZE.value
    global data_section_size
    global text_section_size
    global data_seg
    global text_seg
    # Read each section and put the stream
    lines = input.readlines()
    for line in lines:
        line = line.strip()
        _line = line
        token_line = _line.strip('\n\t').split()
        temp = token_line[0]

        # Check section type
        if temp == ".data":
            cur_section = section.DATA.value
            data_seg = TemporaryFile('w+')
            continue
        elif temp == '.text':
            address = 0
            cur_section = section.TEXT.value
            text_seg = TemporaryFile('w+')
            continue

        # Put the line into each segment stream
        if cur_section == section.DATA.value:
            for t in token_line:
                if t[-1] != ':' and t != '.word':
                    if t[:2] == "0x":
                        t = str(hex_to_num(t))
                    data_seg.write(t)                 #shoud I remove last ' '?
                elif t[-1] == ':':
                    symbol = symbol_t()
                    symbol.name = t[:-1]
                    symbol.address = 268435456 + address   #can I add?
                    symbol_table_add_entry(symbol)
            data_section_size += 1
            data_seg.write('\n')                            #should I remove last '\n'?
        elif cur_section == section.TEXT.value:
            if token_line[0][-1] == ':':
                symbol = symbol_t()
                symbol.name = token_line[0][:-1]
                symbol.address = 4194304 + address       #can I add?
                symbol_table_add_entry(symbol)
                address -= BYTES_PER_WORD
            elif token_line[0] == "la":
                reg = token_line[1] + " "
                dat = token_line[2]
                for sym in SYMBOL_TABLE:
                    if sym.name == dat:
                        adr = num_to_bits(sym.address, 32)
                        break
                text_seg.write("lui " + reg + "0b" + adr[:16] + '\n')
                text_section_size += 1
                if adr[16:] != "0000000000000000":
                    text_seg.write("ori " + reg + reg + "0b" + adr[16:] + '\n')
                    text_section_size += 1
                    address += BYTES_PER_WORD
            else:
                for t in token_line:
                    text_seg.write(t + ' ')             #shoud I remove last ' '?
                text_section_size += 1
                text_seg.write('\n')                        #should I remove last '\n'?
        address += BYTES_PER_WORD


# Record .text section to output file
def record_text_section(output):
    cur_addr = MEM_TEXT_START

    # Point to text_seg stream
    text_seg.seek(0)

    # Print .text section
    lines = text_seg.readlines()
    for line in lines:
        line = line.strip()
        i, idx, type, rs, rt, rd, imm, shamt = 0, 0, '0', 0, 0, 0, 0, 0

        token_line = line.split()
        cur_inst_name = token_line[0]
        for inst in inst_list:
            if cur_inst_name == inst.name:
                type = inst.type
                op = inst.op
                if type == 'R':    
                    fun = inst.funct
                break

        if type == 'R':
            if cur_inst_name == "sll" or cur_inst_name == "srl":
                rs = num_to_bits(0, 5)
                rt = num_to_bits(int(''.join(filter(str.isalnum, token_line[2]))), 5)
                rd = num_to_bits(int(''.join(filter(str.isalnum, token_line[1]))), 5)
                shamt = num_to_bits(int(''.join(filter(str.isalnum, token_line[3]))), 5) 
            elif cur_inst_name == "jr":
                rs = num_to_bits(int(''.join(filter(str.isalnum, token_line[1]))), 5)
                rt = num_to_bits(0, 5)
                rd = num_to_bits(0, 5)
                shamt = num_to_bits(0, 5)
            else:
                rs = num_to_bits(int(''.join(filter(str.isalnum, token_line[2]))), 5)
                rt = num_to_bits(int(''.join(filter(str.isalnum, token_line[3]))), 5)
                rd = num_to_bits(int(''.join(filter(str.isalnum, token_line[1]))), 5)
                shamt = num_to_bits(0, 5)
            output.write(op + rs + rt + rd + shamt + fun)

            if DEBUG:
                log(1, f"0x" + hex(cur_addr)[2:].zfill(
                    8) + f": op: {op} rs:${rs} rt:${rt} rd:${rd} shamt:{shamt} funct:{inst_list[idx].funct}")

        if type == 'I':
            if cur_inst_name == "beq" or cur_inst_name == "bne":
                rs = num_to_bits(int(''.join(filter(str.isalnum, token_line[1]))), 5)
                rt = num_to_bits(int(''.join(filter(str.isalnum, token_line[2]))), 5)
                addr = 1
                for sym in SYMBOL_TABLE:
                    if token_line[3] == sym.name:
                        addr = int(sym.address)
                        break
                addr = (addr - cur_addr - 4) // 4
                imm = num_to_bits(addr , 16)
            elif cur_inst_name == "lui":
                rs = num_to_bits(0, 5)
                rt = num_to_bits(int(''.join(filter(str.isalnum, token_line[1]))), 5)
                if token_line[2][:2] == "0x":
                    imm = num_to_bits(hex_to_num(token_line[2]), 16)
                elif token_line[2][:2] == "0b":
                    imm = token_line[2][2:]
                else:
                    imm = num_to_bits(int(token_line[2]), 16)
            elif cur_inst_name == "ori":
                rs = num_to_bits(int(''.join(filter(str.isalnum, token_line[2]))), 5)
                rt = num_to_bits(int(''.join(filter(str.isalnum, token_line[1]))), 5) 
                if token_line[3][:2] == "0x":
                    imm = num_to_bits(hex_to_num(token_line[3]), 16)
                elif token_line[3][:2] == "0b":
                    imm = token_line[3][2:]
                else:
                    imm = num_to_bits(int(token_line[3]), 16)
            elif cur_inst_name == "lw" or cur_inst_name == "sw":
                t = token_line[2].split('$')
                rs = num_to_bits(int(t[1][:-1]), 5)
                rt = num_to_bits(int(token_line[1][1:-1]), 5)
                imm = num_to_bits(int(t[0][:-1]), 16)
            else:
                rs = num_to_bits(int(''.join(filter(str.isalnum, token_line[2]))), 5)
                rt = num_to_bits(int(''.join(filter(str.isalnum, token_line[1]))), 5) 
                if token_line[3][:2] == "0x":
                    imm = num_to_bits(hex_to_num(token_line[3]), 16)    
                else:   
                    imm = num_to_bits(int(token_line[3]), 16)    
            output.write(op + rs + rt + imm)

            if DEBUG:
                log(1, f"0x" + hex(cur_addr)
                    [2:].zfill(8) + f": op:{op} rs:${rs} rt:${rt} imm:0x{imm}")

        if type == 'J':
            jname = token_line[1]
            jaddress = 'error'
            for sym in SYMBOL_TABLE:
                if jname == sym.name:
                    jaddress = int(sym.address) // 4
                    jaddress = num_to_bits(jaddress, 26)
                    break
            output.write(op + jaddress)

        output.write("\n")
        cur_addr += BYTES_PER_WORD

# Record .data section to output file
def record_data_section(output):
    cur_addr = MEM_DATA_START

    # Point to data segment stream
    data_seg.seek(0)

    # Print .data section
    lines = data_seg.readlines()
    for line in lines:
        token_line = line.split()
        address = int(token_line[0])
        address = num_to_bits(address, 32)
        output.write(address)
        output.write('\n')

        if DEBUG:
            log(1, f"0x" + hex(cur_addr)[2:].zfill(8) + f": {line}")

        cur_addr += BYTES_PER_WORD


# Fill the blanks
def make_binary_file(output):
    if DEBUG:
        # print assembly code of text section
        text_seg.seek(0)
        lines = text_seg.readlines()
        for line in lines:
            line = line.strip()

    if DEBUG:
        log(1,
            f"text size: {text_section_size}, data size: {data_section_size}")

    # Print text section size and data section size
    output.write(num_to_bits(4*text_section_size, 32))
    output.write('\n')
    output.write(num_to_bits(4*data_section_size, 32))
    output.write('\n')
    
    # Print .text section
    record_text_section(output)
    # Print .data section
    record_data_section(output)


################################################
# Function: main
#
# Parameters:
#   argc: the number of argument
#   argv[]: the array of a string argument
#
# Return:
#   return success exit value
#
# Info:
#   The typical main function in Python language.
#   It reads system arguments from terminal (or commands)
#   and parse an assembly file(*.s)
#   Then, it converts a certain instruction into
#   object code which is basically binary code
################################################


if __name__ == '__main__':
    argc = len(sys.argv)
    log(1, f"Arguments count: {argc}")

    if argc != 2:
        log(3, f"Usage   : {sys.argv[0]} <*.s>")
        log(3, f"Example : {sys.argv[0]} sample_input/example.s")
        exit(1)

    # Read the input file
    input_filename = sys.argv[1]
    input_filePath = os.path.join(os.curdir, input_filename)

    if os.path.exists(input_filePath) == False:
        log(3,
            f"No input file {input_filename} exists. Please check the file name and path.")
        exit(1)

    f_in = open(input_filePath, 'r')

    if f_in == None:
        log(3,
            f"Input file {input_filename} is not opened. Please check the file")
        exit(1)

    # Create the output file (*.o)
    output_filename = change_file_ext(sys.argv[1])
    output_filePath = os.path.join(os.curdir, output_filename)

    if os.path.exists(output_filePath) == True:
        log(0, f"Output file {output_filename} exists. Remake the file")
        os.remove(output_filePath)
    else:
        log(0, f"Output file {output_filename} does not exist. Make the file")

    f_out = open(output_filePath, 'w')
    if f_out == None:
        log(3,
            f"Output file {output_filename} is not opened. Please check the file")
        exit(1)

    ################################################
    # Let's compelte the below functions!
    #
    #   make_symbol_table(input)
    #   make_binary_file(output)
    ################################################
    make_symbol_table(f_in)
    
    ################################################
    # At first please make below line as a comments, or it causes error
    ################################################
    make_binary_file(f_out)

    f_in.close()
    f_out.close()
