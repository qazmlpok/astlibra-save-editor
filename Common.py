import csv
import re
import os

class Globals():
    #This should be in a different file or something.
    force = [
        'Fire',     #Red (0x73b4)
        'Earth',    #Yellow
        'Water',    #Blue
        'Darkness', #Purple
        'Wind',     #Green
        'Holy',     #White (0x73c8)
    ]
    force_colors = {
        'red' : 'Fire',    
        'yellow' : 'Earth',   
        'blue' : 'Water',   
        'purple' : 'Darkness',
        'green' : 'Wind',    
        'white' : 'Holy',    
    }
    #The order is top-bottom, left-right
    stats = [
        'HP',           #(0x1168)
        'Attack',
        'Defense',
        'Magic',
        'Agility',
        'Luck',
        'Adaptability', #(0x1180)
    ]
    @staticmethod
    def array_to_field(arr, start, size, prefix):
        """ Convert an array of field names to an array of fields.
        This requires the fields to be sequential within the file - but this is frequently the case.
        """
        ret = []
        for i in range(len(arr)):
            f = arr[i]
            field_name = f'{prefix}_{f.lower()}'
            ret.append(Field(field_name, start + i*size, size))
        return ret

class Field():
    """ Represents a single field with a known size and position
    Uses get/set attr to store the data on the containing object.
    Only int values are supported.
    """
    def __init__(self, field_name, position, size):
        self.field_name = field_name
        self.size = size
        self.position = position
        #self.validator = validator
        #if validator is None:
        #    self.validator = FieldBase.noop
        #if not callable(self.validator):
        #    raise Exception('validator must be a function/lambda')
    def Read(self, dst, filedata):
        #data = fh.readbytes(self.size)
        data = filedata[self.position:self.position+self.size]
        intdata = int.from_bytes(data, 'little', signed=False)
        #if (not self.validator(data)):
        #    raise Exception(f"Validator failed for {self.field_name} with value {data}.")
        setattr(dst, self.field_name, intdata)
    def Write(self, src, filedata):
        data = getattr(src, self.field_name)
        b = data.to_bytes(self.size, 'little')
        #validate on write too?
        filedata[self.position:self.position+self.size] = b

class DataBase():
    """Abstract base class for every container.
    """
    def __init__(self, filedata):
        self.Read(filedata)
        #This should only apply to local fields.
        #I really only care about the duplicate checking, so figure this out later.
        #self.fields_by_name = {}
        #for f in self.GetFields():
        #    if f.field_name in self.fields_by_name:
        #        raise Exception(f"Duplicate field name: {f.field_name}")
        #    self.fields_by_name[f.field_name] = f
    def GetFields(self):
        """ Return every field within this container
        """
        #(This is a function to enable nesting, e.g. with Items)
        return self.fields
    def Read(self, filedata):
        fields = self.GetFields()
        for f in fields:
            f.Read(self, filedata)
    def Write(self, srcdata):
        """ Calls Write on every field. 
        Requires the initial data in order to support sparse writes.
        """
        fields = self.GetFields()
        for f in fields:
            f.Write(self, srcdata)
    def Print(self):
        for f in self.GetFields():
            name = f.field_name
            val = getattr(self, name)
            print(f"{name}: {val}")
#

def open_spreadsheet(fname):
    csvdata = {}
    with open(fname, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            id = row['Id']
            if id[0:2] == '0x':
                id = int(id, 16)
            else:
                id = int(id)
            row['Id'] = id
            csvdata[id] = row
    return csvdata