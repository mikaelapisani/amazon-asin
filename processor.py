#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 23:43:17 2019

@author: mikaelapisanileal
"""
import os
import re
from dropbox_handler import DropboxHandler
import pandas as pd
import logging 
import math
import numpy as np
import csv
import os.path

#return delimiter for a csv data
def get_delimiter(file_path, encoding_data):
        sniffer = csv.Sniffer()
        with open(file_path, 'r', encoding=encoding_data) as csvfile: 
            dialect = sniffer.sniff(csvfile.read(1024), delimiters=";,\t|")
            return dialect.delimiter

#get amount of chunks based on output_size_gb
def get_chunks(output_size_mb, df):
    mem_usage_1 = (round(df.memory_usage(deep=True).sum() / 1024 ** 2, 2))
    return math.trunc(mem_usage_1/output_size_mb)
   
#check if appending the two datasets the size is bigger than output_size_gb
def check_chunks(output_size_mb, df1, df2):
    mem_usage_1 = (round(df1.memory_usage(deep=True).sum() / 1024 ** 2, 2))
    mem_usage_2 = (round(df2.memory_usage(deep=True).sum() / 1024 ** 2, 2))
    chunks = math.trunc((mem_usage_1 + mem_usage_2)/output_size_mb)
    return (chunks > 0)
 

class Processor():
    def __init__(self, conf):
        self.config = conf
        #set logging configuration
        logging.basicConfig(format='%(levelname)s:%(asctime)s - %(message)s')
        self.log = logging.getLogger()
        self.log.setLevel(logging.getLevelName(self.config.log_level))        
        self.dbx = DropboxHandler(self.config.access_token, self.config.dropbox_timeout, self.config.dropbox_chunck)
  
    #upload file to dropbox
    #if there is an error when uploading, files would be located in results path
    def upload_file(self, df, idx):
        filename = self.config.result_prefix + str(idx) + self.config.result_extension
        file_from = self.config.result_folder + filename
        file_to = self.config.dropbox_folder_upload + filename
        print(file_to)
        df.to_csv(file_from, index=False)
        print(file_from)
        self.log.info('Uploading file: %s', file_from)
        upload = True
        try:
           self.dbx.upload_file(file_from, file_to)
        except Exception as err:
            self.log.error('Failed to upload %s\n%s', file_from, err)
            upload = False
        if upload:
           os.remove(file_from)
        return idx+1
        
    #divide file into chunks and upload to dropbox          
    def save_data(self, df, idx):
        chunks = get_chunks(self.config.output_size_mb, df)
        if (chunks==0):
            idx = self.upload_file(df, idx)
        else:
            for chunk in np.array_split(df, chunks):
                idx = self.upload_file(chunk, idx)
        return idx
    
    #read file and return dataframe        
    def create_dataframe(self, local_path):    
        try:
            df = pd.read_csv(local_path, header=0, 
                             sep = get_delimiter(local_path, self.config.encoding_input), 
                             usecols=['asin'	, 'manufacturer','invalid'],
                             dtype={'asin':object,'manufacturer':object,'invalid':object},
                             encoding=self.config.encoding_input)
        except Exception as err:
            self.log.warning('Failed to process file:%s\n%s', local_path, err)
            df = pd.read_excel(local_path, 
                               header=0,  
                             usecols=['asin'	, 'manufacturer','invalid'],
                             dtype={'asin':object,'manufacturer':object,'invalid':object},
                             encoding=self.config.encoding_input)
        return df

    #list all files to process and for each append to df until reach threshold
    #once the threshold is reach, the file is uploaded and start to create another df
    def process_data(self):
        files = self.dbx.list_recursive(self.config.dropbox_folder_download)
        df = pd.DataFrame(data={})
        idx=0
        for file in files:
            matcher = re.compile(self.config.file_regex)
            file_dir = file[0]
            filename = file[1]
            file_path = file_dir + '/' + filename
            if matcher.match(file[1]):
                try:
                    local_path = self.config.data_folder + filename
                    self.dbx.download_file(file_path, local_path)
                    df2 = self.create_dataframe(local_path)
                    if (check_chunks(self.config.output_size_mb, df,df2)):
                        idx = self.save_data(df, idx)
                        df = df2
                    else:
                        df = df.append(df2)
                    os.remove(local_path)
                except Exception as err:
                    self.log.error('Failed processing file %s\n%s', filename, err)

                
        if (df.shape[0]>0):
            self.log.info('Saving last chunck')
            idx = self.save_data(df, idx)  
            
             
