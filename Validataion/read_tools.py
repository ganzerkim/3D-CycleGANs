import numpy as np
import os
import re
from random import shuffle
import tensorflow as tf
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits import mplot3d
import random


class Data:
    def __init__(self,config):
        self.config = config
        self.train_batch_index = 0
        self.test_seq_index = 0

        self.resolution = config['resolution']
        self.batch_size = config['batch_size']
        
        self.train_names = config['train_names']
        self.test_names = config['test_names']

        self.X_train_files, self.Y_train_files = self.load_X_Y_files_paths_all( self.train_names,label='train')
        self.X_test_files, self.Y_test_files = self.load_X_Y_files_paths_all(self.test_names,label='test')
        print "X_train_files:",len(self.X_train_files)
        print "X_test_files:",len(self.X_test_files)

        self.total_train_batch_num = int(len(self.X_train_files) // self.batch_size) -1
        self.total_test_seq_batch = int(len(self.X_test_files) // self.batch_size) -1
	self.batch_name = 'batchname'

    @staticmethod
    def output_Voxels(name, voxels):
        if len(voxels.shape)>3:
            x_d = voxels.shape[0]
            y_d = voxels.shape[1]
            z_d = voxels.shape[2]
            v = voxels[:,:,:,0]
            v = np.reshape(v,(x_d,y_d,z_d))	
        else:
            v = voxels
        x, y, z = np.where(v > 0.5)
	wfile = open(name+'.asc','w')
	for i in range(len(x)):
	    data = str(x[i]) +' '+ str(y[i]) +' '+ str(z[i])
            wfile.write(data + '\n')
        wfile.close()

    @staticmethod
    def plotFromVoxels(name, voxels):
        if len(voxels.shape)>3:
            x_d = voxels.shape[0]
            y_d = voxels.shape[1]
            z_d = voxels.shape[2]
            v = voxels[:,:,:,0]
            v = np.reshape(v,(x_d,y_d,z_d))
        else:
            v = voxels
        #x, y, z = v.nonzero()
	x, y, z = np.where(v > 0.5)
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(x, y, z, zdir='z', c='red')
        plt.savefig(name)
	plt.close()
        #plt.show()

    def load_X_Y_files_paths_all(self, obj_names, label='train'):
        x_str=''
        y_str=''
        if label =='train':
            x_str='X_train_'
            y_str ='Y_train_'

        elif label == 'test':
            x_str = 'X_test_'
            y_str = 'Y_test_'

        else:
            print "label error!!"
            exit()

        X_data_files_all = []
        Y_data_files_all = []
        for name in obj_names:
            X_folder = self.config[x_str + name]
            Y_folder = self.config[y_str + name]
            X_data_files, Y_data_files = self.load_X_Y_files_paths(X_folder, Y_folder)

            for X_f, Y_f in zip(X_data_files, Y_data_files):
                if X_f[0:15] != Y_f[0:15]:
                    print "index inconsistent!!\n"
                    exit()
                X_data_files_all.append(X_folder + X_f)
                Y_data_files_all.append(Y_folder + Y_f)
        return X_data_files_all, Y_data_files_all

    def load_X_Y_files_paths(self,X_folder, Y_folder):
        X_data_files = [X_f for X_f in sorted(os.listdir(X_folder))]
        Y_data_files = [Y_f for Y_f in sorted(os.listdir(Y_folder))]

        return X_data_files, Y_data_files


    def load_single_voxel_grid(self,path):
        temp = re.split('_', path.split('.')[-2])
        x_d = int(temp[len(temp) - 3])
        y_d = int(temp[len(temp) - 2])
        z_d = int(temp[len(temp) - 1])

        a = np.loadtxt(path)
        if len(a)<=0:
            print " load_single_voxel_grid error: ", path
            exit()

        voxel_grid = np.zeros((64, 64, 64,1))
        for i in a:
            voxel_grid[int(i[0]), int(i[1]), int(i[2]),0] = 20 # occupied

        return voxel_grid

    def load_X_Y_voxel_grids(self,X_data_files, Y_data_files):
        if len(X_data_files) !=self.batch_size or len(Y_data_files)!=self.batch_size:
            print "load_X_Y_voxel_grids error:", X_data_files, Y_data_files
            exit()

        X_voxel_grids = []
        Y_voxel_grids = []
        index = -1
        for X_f, Y_f in zip(X_data_files, Y_data_files):
            index += 1
            X_voxel_grid = self.load_single_voxel_grid(X_f)
            X_voxel_grids.append(X_voxel_grid)

            Y_voxel_grid = self.load_single_voxel_grid(Y_f)
            Y_voxel_grids.append(Y_voxel_grid)

        X_voxel_grids = np.asarray(X_voxel_grids)
        Y_voxel_grids = np.asarray(Y_voxel_grids)
        return X_voxel_grids, Y_voxel_grids

    def shuffle_X_Y_files(self, label='train'):
        X_new = []; Y_new = []
        if label == 'train':
            X = self.X_train_files; Y = self.Y_train_files
            self.train_batch_index = 0
            index = range(len(X))
            shuffle(index)
            for i in index:
                X_new.append(X[i])
                Y_new.append(Y[i])
            self.X_train_files = X_new
            self.Y_train_files = Y_new

        elif label == 'test':
            X = self.X_test_files; Y = self.Y_test_files
            self.test_seq_index = 0
            index = range(len(X))
            shuffle(index)
            for i in index:
                X_new.append(X[i])
                Y_new.append(Y[i])
            self.X_test_files = X_new
            self.Y_test_files = Y_new

        else:
            print "shuffle_X_Y_files error!\n"
            exit()

    ###################### voxel grids
    def load_X_Y_voxel_grids_train_next_batch(self):
        X_data_files = self.X_train_files[self.batch_size * self.train_batch_index:self.batch_size * (self.train_batch_index + 1)]
        Y_data_files = self.Y_train_files[self.batch_size * self.train_batch_index:self.batch_size * (self.train_batch_index + 1)]
        self.train_batch_index += 1
	self.batch_name = X_data_files
        X_voxel_grids, Y_voxel_grids = self.load_X_Y_voxel_grids(X_data_files, Y_data_files)
        return X_voxel_grids, Y_voxel_grids

    def load_X_Y_voxel_grids_test_next_batch(self,fix_sample=False):
        if fix_sample:
            random.seed(45)
        idx = random.sample(range(len(self.X_test_files)), self.batch_size)
        X_test_files_batch = []
        Y_test_files_batch = []
        for i in idx:
            X_test_files_batch.append(self.X_test_files[i])
            Y_test_files_batch.append(self.Y_test_files[i])
	self.batch_name = X_test_files_batch
        X_test_batch, Y_test_batch = self.load_X_Y_voxel_grids(X_test_files_batch, Y_test_files_batch)
        return X_test_batch, Y_test_batch
