import sys
import os
from enum import Enum
from tempfile import TemporaryFile
import re
import ctypes

################################################
# For debug option. If you want to debug, set 1
# If not, set 0.
################################################

DEBUG = 0

MAX_SYMBOL_TABLE_SIZE = 1024
MEM_TEXT_START = 0x00400000
MEM_DATA_START = 0x10000000
BYTES_PER_WORD = 4

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


class la_struct:
    def __init__(self, op, rt, imm):
        self.op = op
        self.rt = rt
        self.imm = imm

class section(Enum):
    DATA = 0
    TEXT = 1
    MAX_SIZE = 2


################################################
# Global Variable Declaration
################################################

ADD = inst_t("add", "000000", 'R', "100000")
ADDI = inst_t("addi", "001000", 'I', "")
ADDIU = inst_t("addiu", "001001", "I", "")  # 0
ADDU = inst_t("addu",    "000000", 'R', "100001")  # 1
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
SLT = inst_t("slt", "000000", 'R', "101010")
SLTI = inst_t("slti", "001010", 'I', "")
SLTIU = inst_t("sltiu",    "001011", 'I', "")
SLTU = inst_t("sltu",    "000000", 'R', "101011")
SLL = inst_t("sll",     "000000", 'R', "000000")
SRL = inst_t("srl",     "000000", 'R', "000010")
SW = inst_t("sw",      "101011", 'I', "")
SUB = inst_t("sub", "000000", 'R', "100010")
SUBU = inst_t("subu",    "000000", 'R', "100011")

inst_list = [ADD,  ADDI, ADDIU, ADDU, AND,
             ANDI, BEQ,  BNE,   J,    JAL, 
             JR,   LUI,   LW,   NOR,
             OR,   ORI,  SLT,   SLTI, SLTIU,  
             SLTU, SLL,  SRL,   SW, 
             SUB,  SUBU, ]

symbol_struct = symbol_t()
SYMBOL_TABLE = [symbol_struct] * MAX_SYMBOL_TABLE_SIZE

symbol_table_cur_index = 0

data_section_size = 0
text_section_size = 0


################################################
# Function Declaration
################################################

def change_file_ext(fin_name):
    fname_list = fin_name.split('.')
    fname_list[-1] = 'o'
    fout_name = ('.').join(fname_list)
    return fout_name


def symbol_table_add_entry(symbol):
    global SYMBOL_TABLE
    global symbol_table_cur_index

    SYMBOL_TABLE[symbol_table_cur_index] = symbol
    symbol_table_cur_index += 1
    if DEBUG:
        log(1, f"{symbol.name}: 0x" + hex(symbol.address)[2:].zfill(8))


def convert_label(label):
    address = 0
    for i in range(symbol_table_cur_index):
        if label == SYMBOL_TABLE[i].name:
            address = SYMBOL_TABLE[i].address
            break
    return address


def num_to_bits(num, len):
    bit = bin(num & (2**len-1))[2:].zfill(len)
    return bit

#################################################
# # # # # # # # # # # # # # # # # # # # # # # # #
#                                               #
# Please Do not change the above if possible    #
# The TA's are not resposinble for failures     #
# due to changes in the above                   #
#                                               #
# # # # # # # # # # # # # # # # # # # # # # # # #
#################################################

def make_symbol_table(input):
    size_bit = 0
    address = 0

    cur_section = section.MAX_SIZE.value

    # Read .data section
    lines = input.readlines()
    while len(lines) > 0:
        line = lines.pop(0)
        line = line.strip()
        _line = line
        token_line = _line.strip('\n\t').split()
        temp = token_line[0]

        if temp == ".data":
            '''
            blank
            '''
            cur_section = section.DATA.value
            global data_seg
            data_seg = TemporaryFile('w+')
            continue

        if temp == '.text':
            '''
            blank
            '''
            cur_section = section.TEXT.value
            global text_seg
            text_seg = TemporaryFile('w+')
            continue

        if cur_section == section.DATA.value:
            '''
            blank
            '''
            if temp[-1] == ':':
                symbol = symbol_t()
                symbol.name = temp[:-1]
                symbol.address = ctypes.c_uint(address).value
                symbol_table_add_entry(symbol)

            word = line.find(".word")

            if word != -1:
                data_seg.write("%s\n" % line[word:])

        elif cur_section == section.TEXT.value:
            '''
            blank
            '''
            if temp[-1] == ":":
                symbol = symbol_t()
                symbol.name = temp[:-1]
                symbol.address = ctypes.c_uint(address).value
                symbol_table_add_entry(symbol)
                continue
            
        address += BYTES_PER_WORD

def record_text_section(fout):
    # print text section
    cur_addr = MEM_TEXT_START
    text_seg.seek(0)

    lines = text_seg.readlines()
    for line in lines:
        line = line.strip()
        inst_type, rs, rt, rd, imm, shamt = '0', 0, 0, 0, 0, 0
        
        '''
        blank: Find the instruction type that matches the line
        '''

        if inst_type == 'R':
            '''
            blank
            '''
            if DEBUG:
                log(1, f"0x" + hex(cur_addr)[2:].zfill(
                    8) + f": op: {op} rs:${rs} rt:${rt} rd:${rd} shamt:{shamt} funct:{inst_obj.funct}")

        if inst_type == 'I':
            '''
            blank
            '''

            if DEBUG:
                log(1, f"0x" + hex(cur_addr)
                    [2:].zfill(8) + f": op:{op} rs:${rs} rt:${rt} imm:0x{imm}")

        if inst_type == 'J':
            '''
            blank
            '''
            
            if DEBUG:
                log(1, f"0x" + hex(cur_addr)
                    [2:].zfill(8) + f" op:{op} addr:{addr}")

        fout.write("\n")
        cur_addr += BYTES_PER_WORD


def record_data_section(fout):
    cur_addr = MEM_DATA_START
    data_seg.seek(0)

    lines = data_seg.readlines()
    
    for line in lines:
        '''
        blank
        '''
        line = line.strip()
        token_line = line.strip('\n\t').split()
        data = token_line[-1]
        data = int(data, 0)
        fout.write("%s\n" % num_to_bits(data, 32))

        if DEBUG:
            log(1, f"0x" + hex(cur_addr)[2:].zfill(8) + f": {line}")

        cur_addr += BYTES_PER_WORD


def make_binary_file(fout):
    if DEBUG:
        # print assembly code of text section
        text_seg.seek(0)
        lines = text_seg.readlines()
        for line in lines:
            line = line.strip()

    if DEBUG:
        log(1,
            f"text size: {text_section_size}, data size: {data_section_size}")

    # print text_size, data_size
    '''
    blank: Print text section size and data section size
    '''
    fout.write("%s\n" % num_to_bits(int(text_section_size),32))
    fout.write("%s\n" % num_to_bits(int(data_section_size),32))

    record_text_section(fout)
    record_data_section(fout)

#################################################
# # # # # # # # # # # # # # # # # # # # # # # # #
#                                               #
# Please Do not change the below if possible    #
# The TA's are not resposinble for failures     #
# due to changes in the below code.             #
#                                               #
# # # # # # # # # # # # # # # # # # # # # # # # #
#################################################

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
    make_binary_file(f_out)

    f_in.close()
    f_out.close()
