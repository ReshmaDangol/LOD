import os
file = "drugbank"
directory = "temp_"+file
directory_path = "../data/" + directory
if not os.path.exists(directory_path):
    os.makedirs(directory_path)
with open('../data/lod_files/drugbank.nq') as infp:
    number_of_files = 200
    files = [open(directory_path +'/file%d.nq' % i, 'w') for i in range(number_of_files)]
    for i, line in enumerate(infp):
        files[i % number_of_files].write(line)
    for f in files:
        f.close()