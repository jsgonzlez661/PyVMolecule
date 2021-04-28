#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2021 Jose Gonzalez ~ All rights reserved. MIT license.

import json
import os

from openbabel import pybel


class MoleculeLoad:

    def __init__(self, file):
        self.file = file
        self.ext = os.path.splitext(self.file)[1].replace('.', '')
        self.data = self.open_json()

    @staticmethod
    def open_json():
        with open('data.json') as file:
            data = json.load(file)
        return data

    def load(self):
        coordinates = []
        radios = []
        colors = []
        # atomic_num = []

        for molecule in pybel.readfile(self.ext, self.file):
            mol = molecule.atoms
            for m in mol:
                for d in self.data['data']:
                    if m.atomicnum == d['atomic_number']:
                        coordinates.append(list(m.coords))
                        if d['van_der_walls'] == "no data":
                            radios.append(1.5)
                        else:
                            radios.append(d['van_der_walls'])
                        colors.append(d['colors'])
                        # atomic_num.append(d['atomic_number'])

        return coordinates, radios, colors  # , atomic_num

    def connect(self):
        list_connect = []
        for molecule in pybel.readfile(self.ext, self.file):
            smart = pybel.Smarts("*~*")  # Any bond in molecule
            for bond in smart.findall(molecule):
                list_connect.append(bond)
        return list_connect
