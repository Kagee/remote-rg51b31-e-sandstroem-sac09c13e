#! /usr/bin/python3

import re
import sys
from bitstring import BitArray
from termcolor import colored

SHORT = 560
LONG = 1690

def print_bytes(parsed_seg):
    for x in parsed_seg:
        if not x:
            return
        for bit in list(x.bin):
            if bit == "0":
                print(colored(bit, "red"), end=" ")
            else: 
                print(colored(bit, "green"), end=" ")
        print("- ", end="")
    print()

def parse_seg(seg):
    assert(len(seg) == 97)
    #print(len(seg))
    #print(seg)
    seg = iter(seg)
    c = 1
    n = ""
    DESC = ["ADDRESS", "!ADDRESS", "COMMAND", "!COMMAND", "UNKNOWN1", "!UNKNOWN2"]
    data = []
    d = 0
    for num in seg:
        try:
            first = num
            second = next(seg)
            if first == SHORT and second == SHORT:
                #print("0", end="")
                n += "0"
            elif first == SHORT and second == LONG:
                #print("1", end="")
                n += "1"
            else:
                #print(f"what? {n}")
                sys.exit()
            if c % 8 == 0:
                b = BitArray(bin=n)
                data.append(b)
                #print(f" - { b.uint } - { DESC[d] }")
                d += 1
                n = ""
            c = c + 1
        except StopIteration:
            #print()
            #print(f"StopIteration")
            data[1].invert()
            assert(data[0] == data[1])
            ADDR = data[0]

            data[3].invert()
            assert(data[2] == data[3])
            CMD = data[2]

            data[5].invert()
            if (data[4] != data[5]):
                #print(f"unknown 1: {data[4].bin}")
                #print(f"unknown 2: {data[5].bin}")
                print(colored("dual", "blue"))
                print_bytes((data[0], data[2], data[4]))
                #print()
                print_bytes((data[1], data[3], data[5]))
                #print()
                return (None, None, None)

            UNKN = data[4]
            #print(f"ADR: { ADDR.bin }")
            #print(f"CMD: { CMD.bin }")
            #print(f"UNK: { UNKN.bin }")
            return ADDR, CMD, UNKN 


def parse_numbers(numbers):
    header = numbers[0:2]
    footer = numbers[-2:]
    numbers = [ int(x) for x in numbers[2:-2] ]
    #print(header)
    #print(footer)
    #print(numbers, len(numbers))
    seg = []
    parsed_seg = []
    for num in numbers:
        if num > (SHORT - 200) and num < (SHORT + 200):
            num = SHORT
            seg.append(num)
        elif num > (LONG - 200) and num < (LONG + 200):
            num = LONG
            seg.append(num)
        else:
            if len(seg):
                parsed_seg.append(parse_seg(seg))
            num = f".{num}."
            seg = []
            continue
        #print(num, end=" ")
    #print("SEG:" ,seg)
    parsed_seg.append(parse_seg(seg))
    #print("PARSEG:", parsed_seg)
    if len(parsed_seg) > 1:
        # Noen kommandoer kan ikke repeteres (swing, led on/off)
        # og sendes derfor ikke flere ganger
        assert(parsed_seg[0] == parsed_seg[1])
    #print(parsed_seg[0])
    print_bytes(parsed_seg[0])
    #for x in parsed_seg[0]:
    #    for bit in list(x.bin):
    #        if bit == "0":
    #            print(colored(bit, "red"), end=" ")
    #        else: 
    #            print(colored(bit, "green"), end=" ")
    #    print("- ", end="")

with open(sys.argv[1]) as fp:
    lines = fp.read().splitlines()
    lines = iter([ x.strip() for x in lines ])
    for line in lines:
        try:
            #print("searching for space:", line)
            m = re.search(r"^(\d*)-space$", line)
            if m:
                #print('### START (', m.group(1), ') ###')
                line = next(lines)
                assert(line == "")
                numbers = []
                while True:
                    try:
                        line = next(lines)
                    except StopIteration:
                        line = ""
                    if line == "":
                        break
                    numbers += line.split()
                l = len(numbers)
                if l not in [ 201, 200, 101, 100 ]:
                    # We are not really parsing the -pulse and -space correctly,
                    # there is no new press after the last, so is has no -space until
                    # the next, thus 200 (100 = not repeated, swing, led)
                    # print(f"Found only { len(numbers) }, not 200/201, corrupt/invalid list, ignoring")
                    pass
                else:
                    if len(numbers) == 200:
                        numbers += ["-"]
                    parse_numbers(numbers)
                #print('### END ###')
        except AssertionError as ae:
            print(ae)
            print("? ? ? ? ? ? ? ? - ? ? ? ? ? ? ? ? -")
            #pass
    print()
