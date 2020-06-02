import os

class M3UA_Creater:
    def __init__(self):
        self.SUPATH = 'C:\\Sandbox\\m3ua\\'
        self.M3UA_Header1 = '01 00 01 01 00 00 00 '
        self.M3UA_Header2 = '02 10 00 '
        self.M3UA_Header3 = '00 00 02 01\n00 00 2f 01 03 02 00 07'

    def GenerateM3UAForSU(self):
        for parent, dirnames, filenames in os.walk(self.SUPATH):
            for filename in filenames:
                with open(self.SUPATH + filename,'r') as input_SUFile:
                    with open(self.SUPATH + filename + '_new', 'w') as output_SUFile:
                        lines = input_SUFile.readlines()
                        SU_Bytes = []
                        for line in lines:
                            SU_Bytes += line.strip().split(' ')
                        ByteCount = 0

                        # M3UA header
                        dataLength2 = len(SU_Bytes) + 0x10
                        dataLength1 = dataLength2 + ( len(SU_Bytes) % 4 ) + 8
                        output_SUFile.write('# BINARY\n')
                        output_SUFile.write('# DATA M3UA\n')
                        output_SUFile.write( self.M3UA_Header1 )
                        output_SUFile.write( hex(dataLength1)[2:] + ' ' )
                        output_SUFile.write( self.M3UA_Header2 )
                        output_SUFile.write( hex(dataLength2)[2:] + ' ' )
                        output_SUFile.write( self.M3UA_Header3 )
                        output_SUFile.write( '\n' )

                        # Dump single SU
                        output_SUFile.write( '# SU body bytes\n' )
                        for singleByte in SU_Bytes:
                            output_SUFile.write( singleByte )
                            ByteCount += 1
                            if ( ByteCount % 16 ) == 0:
                                output_SUFile.write( '\n' )
                            else:
                                output_SUFile.write( ' ' )

                        # Check if it needs to add padding bytes
                        output_SUFile.write( '\n' )
                        output_SUFile.write( '# padding bytes\n' )
                        for i in range( 0, ( len(SU_Bytes) % 4 ) ):
                            output_SUFile.write( '00 ' )
                            SU_Bytes.append( '00' )

if __name__ == '__main__':
    suM3UA_Creater = M3UA_Creater()

    suM3UA_Creater.GenerateM3UAForSU()