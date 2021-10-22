

from cluplus.proxy import ProxyException

ProxyException.__name__
ProxyException.__module__

module = __import__('cluplus.proxy')

getattr(__builtins__, 'Exception')("kkk")

def exceptionFromStringWithValue(value_string, type_name='Exception', module_name='builtins'):        
    try:
       module = sys.modules[module_name] if module_name in sys.modules else __import__(module_name, fromlist=type_name)
       return getattr(module, type_name)(value_string)
    except AttributeError:
       return Exception(f'Unknown exception type {type_name} - {value_string}')
    except ImportError:
       return Exception(f'Unknown module type {module_name} - {type_name}: {value_string}')


exceptionFromStringWithValue("test") 
exceptionFromStringWithValue("test",'ValueError')
exceptionFromStringWithValue("test",'ProxyException','cluplus.proxy')

#https://click.palletsprojects.com/en/8.0.x/parameters/#implementing-custom-types


import numpy as np
from astropy.io import fits
import jsonpickle


bright = np.rec.array([(1,'Sirius', -1.45, 'A1V'),
                       (2,'Canopus', -0.73, 'F0Ib'),
                       (3,'Rigil Kent', -0.1, 'G2V')],
                       formats='int16,a20,float32,a10',
                       names='order,name,mag,Sp')


a=jsonpickle.encode(bright,make_refs=False)
b=jsonpickle.decode(a)

assert((bright==b).all())


counts = np.array([312, 334, 308, 317])
names = np.array(['NGC1', 'NGC2', 'NGC3', 'NGC4'])
values = np.arange(2*2*4).reshape(4, 2, 2)
col1 = fits.Column(name='target', format='10A', array=names)
col2 = fits.Column(name='counts', format='J', unit='DN', array=counts)
col3 = fits.Column(name='notes', format='A10')
col4 = fits.Column(name='spectrum', format='10E')
col5 = fits.Column(name='flag', format='L', array=[True, False, True, True])
col6 = fits.Column(name='intarray', format='4I', dim='(2, 2)', array=values)

coldefs = fits.ColDefs([col1, col2, col3, col4, col5, col6])
hdu = fits.BinTableHDU.from_columns(coldefs)

col_s = jsonpickle.encode(hdu.columns)
col_n = jsonpickle.decode(col_s)

hdu_n = fits.BinTableHDU.from_columns(col_n)


