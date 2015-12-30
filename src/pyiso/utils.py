# Copyright (C) 2015  Chris Lalancette <clalancette@gmail.com>

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation;
# version 2.1 of the License.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

'''
Various utilities for PyIso.
'''

import socket

import sendfile

from pyisoexception import *

def swab_32bit(input_int):
    '''
    A function to swab a 32-bit integer.

    Parameters:
     input_int - The 32-bit integer to swab.
    Returns:
     The swabbed version of the 32-bit integer.
    '''
    return socket.htonl(input_int)

def swab_16bit(input_int):
    '''
    A function to swab a 16-bit integer.

    Parameters:
     input_int - The 16-bit integer to swab.
    Returns:
     The swabbed version of the 16-bit integer.
    '''
    return socket.htons(input_int)

def ceiling_div(numer, denom):
    '''
    A function to do ceiling division; that is, dividing numerator by denominator
    and taking the ceiling.

    Parameters:
     numer - The numerator for the division.
     denom - The denominator for the division.
    Returns:
     The ceiling after dividing numerator by denominator.
    '''
    # Doing division and then getting the ceiling is tricky; we do upside-down
    # floor division to make this happen.
    # See https://stackoverflow.com/questions/14822184/is-there-a-ceiling-equivalent-of-operator-in-python.
    return -(-numer // denom)

def hexdump(st):
    '''
    A utility function to print a string in hex.

    Parameters:
     st - The string to print.
    Returns:
     A string containing the hexadecimal representation of the input string.
    '''
    return ':'.join(x.encode('hex') for x in st)

def copy_data(data_length, blocksize, infp, outfp):
    '''
    A utility function to copy data from the input file object to the output
    file object.  This function will use the most efficient copy method available,
    which is often sendfile.

    Parameters:
     data_length - The amount of data to copy.
     blocksize - How much data to copy per iteration.
     infp - The file object to copy data from.
     outfp - The file object to copy data to.
    Returns:
     Nothing.
    '''
    if hasattr(infp, 'fileno') and hasattr(outfp, 'fileno'):
        # This is one of those instances where using the file object and the
        # file descriptor causes problems.  The sendfile() call actually updates
        # the underlying file descriptor, but the file object does not know
        # about it.  To get around this, we instead get the offset, allow
        # sendfile() to update the offset, then manually seek the file object
        # to the right location.  This ensures that the file object gets updated
        # properly.
        in_offset = infp.tell()
        out_offset = outfp.tell()
        sendfile.sendfile(outfp.fileno(), infp.fileno(), in_offset, data_length)
        infp.seek(in_offset + data_length)
        outfp.seek(out_offset + data_length)
    else:
        left = data_length
        readsize = blocksize
        while left > 0:
            if left < readsize:
                readsize = left
            outfp.write(infp.read(readsize))
            left -= readsize

def utf_encode_space_pad(instr, length):
    '''
    A function to take an input string and a length, encode the string
    according to utf-16_be, and then pad out the string to the length
    passed in with utf-16_be encoded spaces.

    Parameters:
     instr - The input string to encode and pad.
     length - The length to pad the input string to.
    Returns:
     The input string encoded in utf-16_be and padded with utf-16_be encoded spaces.
    '''
    output = instr.encode('utf-16_be')
    if len(output) > length:
        raise PyIsoException("Input string too long!")

    encoded_space = ' '.encode('utf-16_be')

    left = length - len(output)
    while left > 0:
        if left >= 2:
            output += encoded_space
            left -= 2
        else:
            output += encoded_space[:1]
            left -= 1

    return output