#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
/*
 * This file is part of the Pico Fido distribution (https://github.com/polhenarejos/pico-fido).
 * Copyright (c) 2022 Pol Henarejos.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, version 3.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 */
"""

import sys
import argparse
import platform
from binascii import hexlify
from words import words

try:
    from fido2.ctap2.config import Config
    from fido2.ctap2 import Ctap2
    from fido2.hid import CtapHidDevice
    from fido2.utils import bytes2int, int2bytes
except:
    print('ERROR: fido2 module not found! Install fido2 package.\nTry with `pip install fido2`')
    sys.exit(-1)

try:
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
    from cryptography.hazmat.primitives import hashes
except:
    print('ERROR: cryptography module not found! Install cryptography package.\nTry with `pip install cryptography`')
    sys.exit(-1)

from enum import IntEnum
from binascii import hexlify

if (platform.system() == 'Windows'):
    from secure_key import windows as skey
elif (platform.system() == 'Linux'):
    from secure_key import linux as skey
elif (platform.system() == 'Darwin'):
    from secure_key import macos as skey
else:
    print('ERROR: platform not supported')
    sys.exit(-1)

class VendorConfig(Config):

    class PARAM(IntEnum):
        VENDOR_COMMAND_ID         = 0x01
        VENDOR_AUT_KEY_AGREEMENT  = 0x02
        VENDOR_AUT_CT             = 0x03

    class CMD(IntEnum):
        CONFIG_AUT           = 0x03e43f56b34285e2
        CONFIG_KEY_AGREEMENT = 0x1831a40f04a25ed9
        CONFIG_UNLOCK        = 0x54365966c9a74770
        CONFIG_BACKUP        = 0x6b1ede62beff0d5e

    class RESP(IntEnum):
        KEY_AGREEMENT = 0x01
        BACKUP        = 0x01

    def __init__(self, ctap, pin_uv_protocol=None, pin_uv_token=None):
        super().__init__(ctap, pin_uv_protocol, pin_uv_token)

    def _get_key_device(self):
        return skey.get_secure_key()

    def _get_shared_key(self):
        ret = self._call(
            Config.CMD.VENDOR_PROTOTYPE,
            {
                VendorConfig.PARAM.VENDOR_COMMAND_ID: VendorConfig.CMD.CONFIG_KEY_AGREEMENT,
            },
        )
        peer_cose_key = ret[VendorConfig.RESP.KEY_AGREEMENT]

        sk = ec.generate_private_key(ec.SECP256R1())
        pn = sk.public_key().public_numbers()
        pb = sk.public_key().public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
        key_agreement = {
            1: 2,
            3: -25,  # Per the spec, "although this is NOT the algorithm actually used"
            -1: 1,
            -2: int2bytes(pn.x, 32),
            -3: int2bytes(pn.y, 32),
        }

        x = bytes2int(peer_cose_key[-2])
        y = bytes2int(peer_cose_key[-3])
        pk = ec.EllipticCurvePublicNumbers(x, y, ec.SECP256R1()).public_key()
        shared_key = sk.exchange(ec.ECDH(), pk)

        xkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=12+32,
            salt=None,
            info=pb
        )
        kdf_out = xkdf.derive(shared_key)
        key_enc = kdf_out[12:]
        iv = kdf_out[:12]
        return iv, key_enc, key_agreement, pb

    def _send_command_key(self, cmd):
        iv, key_enc, key_agreement, pb = self._get_shared_key()

        chacha = ChaCha20Poly1305(key_enc)
        ct = chacha.encrypt(iv, self._get_key_device(), pb)
        self._call(
            Config.CMD.VENDOR_PROTOTYPE,
            {
                VendorConfig.PARAM.VENDOR_COMMAND_ID: cmd,
                VendorConfig.PARAM.VENDOR_AUT_KEY_AGREEMENT: key_agreement,
                VendorConfig.PARAM.VENDOR_AUT_CT: ct
            },
        )

    def enable_device_aut(self):
        self._send_command_key(VendorConfig.CMD.CONFIG_AUT)

    def unlock_device(self):
        self._send_command_key(VendorConfig.CMD.CONFIG_UNLOCK)

    def disable_device_aut(self):
        self._call(
            Config.CMD.VENDOR_PROTOTYPE,
            {
                VendorConfig.PARAM.VENDOR_COMMAND_ID: VendorConfig.CMD.CONFIG_AUT,
            },
        )

    def backup_save(self, filename):
        ret = self._call(
            Config.CMD.VENDOR_PROTOTYPE,
            {
                VendorConfig.PARAM.VENDOR_COMMAND_ID: VendorConfig.CMD.CONFIG_BACKUP,
            },
        )
        data = ret[VendorConfig.RESP.BACKUP]
        d = int.from_bytes(skey.get_secure_key(), 'big')
        with open(filename, 'wb') as fp:
            fp.write(b'\x01')
            fp.write(data)
            pk = ec.derive_private_key(d, ec.SECP256R1())
            signature = pk.sign(data, ec.ECDSA(hashes.SHA256()))
            fp.write(signature)
        print('Remember the following words in this order:')
        for c in range(24):
            coef = (d//(2048**c))%2048
            print(f'{(c+1):02d} - {words[coef]}')

    def backup_load(self, filename):
        d = 0
        if (d == 0):
            for c in range(24):
                word = input(f'Introduce word {(c+1):02d}: ')
                while (word not in words):
                    word = input(f'Word not found. Please, tntroduce the correct word {(c+1):02d}: ')
                coef = words.index(word)
                d = d+(2048**c)*coef

        pk = ec.derive_private_key(d, ec.SECP256R1())
        pb = pk.public_key()
        with open(filename, 'rb') as fp:
            format = fp.read(1)[0]
            if (format == 0x1):
                data = fp.read(60)
                signature = fp.read()
            pb.verify(signature, data, ec.ECDSA(hashes.SHA256()))
        skey.set_secure_key(pk)
        self._call(
            Config.CMD.VENDOR_PROTOTYPE,
            {
                VendorConfig.PARAM.VENDOR_COMMAND_ID: VendorConfig.CMD.CONFIG_BACKUP,
                VendorConfig.PARAM.VENDOR_AUT_CT: data,
            },
        )

def parse_args():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(title="commands", dest="command")
    parser_secure = subparser.add_parser('secure', help='Manages security of Pico Fido.')
    parser_secure.add_argument('subcommand', choices=['enable', 'disable', 'unlock'], help='Enables, disables or unlocks the security.')

    parser_backup = subparser.add_parser('backup', help='Manages the backup of Pico Fido.')
    parser_backup.add_argument('subcommand', choices=['save', 'load'], help='Saves or loads a backup.')
    parser_backup.add_argument('filename', help='File to save or load the backup.')

    args = parser.parse_args()
    return args

def secure(dev, args):
    vcfg = VendorConfig(Ctap2(dev))

    if (args.subcommand == 'enable'):
        vcfg.enable_device_aut()
    elif (args.subcommand == 'unlock'):
        vcfg.unlock_device()
    elif (args.subcommand == 'disable'):
        vcfg.disable_device_aut()

def backup(dev, args):
    vcfg = VendorConfig(Ctap2(dev))

    if (args.subcommand == 'save'):
        vcfg.backup_save(args.filename)
    elif (args.subcommand == 'load'):
        vcfg.backup_load(args.filename)


def main(args):
    print('Pico Fido Tool v1.2')
    print('Author: Pol Henarejos')
    print('Report bugs to https://github.com/polhenarejos/pico-fido/issues')
    print('')
    print('')

    dev = next(CtapHidDevice.list_devices(), None)

    if (args.command == 'secure'):
        secure(dev, args)
    elif (args.command == 'backup'):
        backup(dev, args)

def run():
    args = parse_args()
    main(args)

if __name__ == "__main__":
    run()