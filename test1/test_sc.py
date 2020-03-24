#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
import os
from tensorflow.python import pywrap_tensorflow

checkpoint_path = '../srcnn/checkpoint/SRCNN.model-10544000'
reader = pywrap_tensorflow.NewCheckpointReader(checkpoint_path)
var_to_shape_map = reader.get_variable_to_shape_map()
for key in var_to_shape_map:
    print("tensor_name: ", key, end=' ')
    print(reader.get_tensor(key))
'''
