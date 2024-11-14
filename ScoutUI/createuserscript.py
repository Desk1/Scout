def concatenate_files(file_list, output_file):
    with open(output_file, 'wb') as outfile:
        for fname in file_list:
            with open(fname, 'rb') as infile:
                outfile.write(infile.read())


file_list = [
    'src/userscript.js',
    'dist/script.js'
]
output_file = 'userscript.user.js'

concatenate_files(file_list, output_file)
