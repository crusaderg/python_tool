import os
import time

FILE_DIR = 'C:\\Sandbox\\tmp'

def ExtractTimeStamp( fileName ):
    timeStamp = ''

    return fileName.split('_')[3].split('.')[0]
#---------------------------------------------

def ChangeFileName( old_timeStamp, new_TimeStamp ):
    old_FileName = str.format( 'nstc_172.16.66.29_8100_%s.ctrl' % old_timeStamp )
    new_FileName = str.format( 'nstc_172.16.66.29_8100_%s.ctrl' % new_TimeStamp )
    os.rename( FILE_DIR + '\\' + old_FileName, FILE_DIR + '\\' + new_FileName )

    old_FileName = str.format( 'nstc_172.16.66.29_8100_%s.tc_status' % old_timeStamp )
    new_FileName = str.format( 'nstc_172.16.66.29_8100_%s.tc_status' % new_TimeStamp )
    os.rename( FILE_DIR + '\\' + old_FileName, FILE_DIR + '\\' + new_FileName )

    old_FileName = str.format( 'nstc_172.16.66.29_8100_%s.cpi' % old_timeStamp )
    new_FileName = str.format( 'nstc_172.16.66.29_8100_%s.cpi' % new_TimeStamp )
    os.rename( FILE_DIR + '\\' + old_FileName, FILE_DIR + '\\' + new_FileName )

    print( 'Changed file name time stamp from %s to %s!!!' % ( old_timeStamp, new_TimeStamp ) )
#---------------------------------------------

while ( True ):
    now = int( str( time.time() ).split(".")[0] )
    new_TimeStamp = str(now - now % 300)
    old_timeStamp = '0'
    for root, dirs, files in os.walk( FILE_DIR ):
        old_timeStamp = ExtractTimeStamp( files[0] )
        break

    if new_TimeStamp != old_timeStamp:
        ChangeFileName( old_timeStamp, new_TimeStamp )

    time.sleep(10)