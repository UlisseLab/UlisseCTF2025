from ctypes import *

class Transaction(Structure):
    _fields_ = [
        ('sender_balance', c_int64),
        ('amount', c_int64),
        ('note', c_char_p),
    ]
    def __init__(self, id, *args, **kw):
        super().__init__(*args, **kw)
        self.id = id
        
class Result(Structure):
    _fields_ = [
        ('note', c_char_p),
        ('status', c_char_p),
    ]