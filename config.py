#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 08:40:31 2019

@author: mikaelapisanileal
"""

from properties.p import Property


class Config:
    def __init__(self, path):
        prop = Property()
        config = prop.load_property_files(path)
        self.log_level = config['log_level']
        self.access_token = config['access_token']
        self.output_size_mb=int(config['output_size_mb'])
        self.dropbox_folder_download=config['dropbox_folder_download']
        self.dropbox_folder_upload=config['dropbox_folder_upload']
        self.dropbox_chunck=int(config['dropbox_chunck'])
        self.dropbox_timeout=float(config['dropbox_timeout'])
        self.data_folder=config['data_folder']
        self.result_folder=config['result_folder']
        self.file_regex=config['file_regex']
        self.result_prefix=config['result_prefix']
        self.result_extension=config['result_extension']
        
