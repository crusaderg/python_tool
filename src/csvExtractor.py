import glob
import os

CSV_FILE_PATH = 'C:\\tmp\\'
#   extract the columns
interested_Columns = ('calling_address', 'called_address', 'subscriber_phone_number',
                      'direction_name', 'branch_id', 'message_id')

def files( curr_dir, ext ):
    print(os.path.join( curr_dir, ext ))
    for i in glob.glob( os.path.join( curr_dir, ext ) ):
        yield i

#   Remove the previouse extracted result
for i in files( CSV_FILE_PATH, '*.extracted_result.csv' ):
    print( 'Removed file' + i )
    os.remove( i )

for root, dirs, files in os.walk(CSV_FILE_PATH):
    for file in files:
        #   Get the file extension
        file_Extension = file.split( '.' )
        if file_Extension[len(file_Extension) - 1] != 'csv':
            continue

        input_FileName  = CSV_FILE_PATH + file
        output_FileName = CSV_FILE_PATH + file[ : file.rindex( '.csv' ) ] + '.extracted_result.csv'
        
        interested_Columns_Position = {}
        with open(input_FileName, 'r') as input_csvFile:
            with open(output_FileName, 'w') as output_csvFile:
                lines = input_csvFile.readlines()

                columns = lines[0].split(',')
                valid_Column_size = len(columns)
                output_column = ''
                for column in interested_Columns:
                    if (column in columns):
                        interested_Columns_Position[column] = columns.index(column)
                        output_column += column + ','
                if len(output_column) != 0:
                    output_csvFile.write(output_column + '\n')

                for line in lines[1:]:
                    line = "".join(line.split())
                    values = line.split(',')
                    if (len(values) != valid_Column_size):
                        continue
                    output_Record = ''
                    for column in interested_Columns:
                        output_Record += values[interested_Columns_Position[column]] + ','
                    if len(output_Record) != 0:
                        output_csvFile.write(output_Record + '\n')

print('Done!!!')



