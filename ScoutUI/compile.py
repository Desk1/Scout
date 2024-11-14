def concatenate_files(file_list, output_file):
    with open(output_file, 'wb') as outfile:
        for fname in file_list:
            with open(fname, 'rb') as infile:
                outfile.write(infile.read())


file_list = [
    'src/extensions/ccindicator.js',
    'src/extensions/characterpanel.js',
    'src/extensions/chat.js',
    'src/extensions/revindicator.js',
    'src/extensions/settings.js',
    'src/extensions/skillpresets.js',
    
	'src/main.js'
]
output_file = 'dist/bundle.js'

concatenate_files(file_list, output_file)
