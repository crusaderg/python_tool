CSV_FILE_PATH = 'C:\\tmp\\'

CSV_FILE_NAME = 'control_plane_wireline_service.csv'
SERVICE_FILE_NAME = 'control_plane_wireline_service.xml'

EXPOERT_MAPPING_PREFIX = 'CP'
D_MAPPING_EXPOERT_MAPPING_PREFIX = 'CPX'
MEASURE__EXPOERT_MAPPING_PREFIX = 'CPM'
BLANK = '    '
EOL = '\n'

Current_Processing     = 0
PROCESS_SERVICEHEADER  = 1
PROCESS_DIMENSION      = 2
PROCESS_MESSURE        = 3

SERVICE_MODEL_NAME     = 'service name'
DIMENSION_COLUMN_NAME  = 'dimension column name'
MEASURE_COLUMN_NAME    = 'measure column name'

class ServiceBasicItem:
    def __init__(self):
        self.attributes = {}

class DimensionItem(ServiceBasicItem):
    dimensions = []
    export_mapping_index = 1
    d_mapping_export_mapping_index = 1
#----------------------------------------------

class MeasureItem(ServiceBasicItem):
    measures = []
    export_mapping_index = 1
    def __init__(self):
        super().__init__()
        self.input_field = ''
        self.constant_value = ''
# ----------------------------------------------

class Pair:
    def __init__(self):
        self.first = ''
        self.second = ''
# ----------------------------------------------

class DimensionMappingItem:
    dimension_mappings = []
    output_to_service_dimenstion_names = []
    def __init__(self):
        self.dimension_mapping_name = ''
        self.dimension_mapping_items = []
    # ----------------------------------------------
    def IsDimensionOutput(mappings):
        for pair in mappings:
            if not pair.first in DimensionMappingItem.output_to_service_dimenstion_names:
                return False
        return True
    # ----------------------------------------------
# ----------------------------------------------

def CombineColumneAndValue(columns, values, basic_item):
    for i in range(0 , len(columns)):
        basic_item.attributes[ str.lower( columns[i] ) ] = values[i]
# ----------------------------------------------

def WriteServiceModelHeader(dimension_output_file, service):
    header = """<?xml-model href="../../schemas/every_model.sch" type="application/xml" schematypens="http://purl.oclc.org/dsdl/schematron"?>"""
    header += EOL
    header += """<service xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance\""""
    header += ' name="' + service.attributes[SERVICE_MODEL_NAME] + '"'
    header += ' type="' + service.attributes['service type'] + '"'
    header += """ xsi:noNamespaceSchemaLocation="../../schemas/xsd/Service.xsd">"""
    dimension_output_file.write(header + EOL)
#----------------------------------------------

def WriteServiceModelInputField(dimension_output_file, dimension_column):
    content = BLANK + '<input-field'
    content += ' name="' + dimension_column.attributes['input'] + '"'
    content += ' type="' + dimension_column.attributes['type'] + '"'
    if dimension_column.attributes['description'] == '':
        content += '/>'
    else:
        content += ' description="' + dimension_column.attributes['description'] + '"/>'
    dimension_output_file.write(content + EOL)
# ----------------------------------------------

def WriteServiceModelDimensionMapping(dimension_output_file):
    for item in DimensionMappingItem.dimension_mappings[:]:
        if DimensionMappingItem.IsDimensionOutput(item.dimension_mapping_items):
            content = BLANK + '<dimension-mapping'
            content += ' dimension="' + item.dimension_mapping_name + '">'
            dimension_output_file.write(content + EOL)
            for each_mapping in item.dimension_mapping_items:
                content = BLANK + BLANK + '<mapping'
                content += ' column="' + each_mapping.first +'"'
                content += ' primary-key="' + each_mapping.first + '"/>'
                dimension_output_file.write(content + EOL)
            dimension_output_file.write(BLANK + '</dimension-mapping>' + EOL)
            # Remove this mapping
            DimensionMappingItem.dimension_mappings.remove(item)
# ----------------------------------------------

def WriteServiceModelDimensionColumn(dimension_output_file, dimension_column):
    content = BLANK + '<dimension-column'
    content += ' column-name="' + dimension_column.attributes[DIMENSION_COLUMN_NAME] + '"'
    if ( str.lower(dimension_column.attributes['type']) == "string" ):
        content += ' column-size="' + dimension_column.attributes['size'] + '"'
    content += ' column-type="' + dimension_column.attributes['type'] + '"'
    content += ' description="' + dimension_column.attributes['description'] + '"'
    content += ' encoding="'    + dimension_column.attributes['encoding'] + '"'
    if dimension_column.attributes['dimension mapping'] == '':
        content += ' export-mapping="' + EXPOERT_MAPPING_PREFIX + str(DimensionItem.export_mapping_index) + '"/>'
        DimensionItem.export_mapping_index += 1
    else:
        content += ' export-mapping="' + D_MAPPING_EXPOERT_MAPPING_PREFIX + str(DimensionItem.d_mapping_export_mapping_index) + '"/>'
        DimensionItem.d_mapping_export_mapping_index += 1
    dimension_output_file.write(content + EOL)
    DimensionMappingItem.output_to_service_dimenstion_names.append(dimension_column.attributes[DIMENSION_COLUMN_NAME])

    content = BLANK + BLANK + '<input-field'
    content += ' ref="' + dimension_column.attributes['input'] + '"/>'
    dimension_output_file.write(content + EOL)

    dimension_output_file.write(BLANK + '</dimension-column>' + EOL)

    # Check and output the dimension mapping
    WriteServiceModelDimensionMapping(dimension_output_file)
# ----------------------------------------------

def WriteServiceModelDimensions(dimension_output_file, dimension_columns):
    # Write the input fields
    dimension_output_file.write(BLANK + '<aging retention-policy="raw.hst"/>' + EOL)
    dimension_output_file.write(BLANK + '<input-field name="segmentation_key" type="INT"/>' + EOL)
    for dimension_column in dimension_columns:
        if dimension_column.attributes['input'] != '':
            WriteServiceModelInputField(dimension_output_file, dimension_column)
    # Write the dimension columns
    dimension_output_file.write(EOL)
    dimension_output_file.write(BLANK + '<timestamp-column encoding="RLE">' + EOL)
    dimension_output_file.write(BLANK + BLANK + '<input-field ref="fileStartTime"/>' + EOL)
    dimension_output_file.write(BLANK + '</timestamp-column>' + EOL)
    dimension_output_file.write(BLANK + '<dimension-column column-name="segmentation_key" column-type="INT" description="Segmentation Key" encoding="DELTAVAL">' + EOL)
    dimension_output_file.write(BLANK + BLANK + '<input-field ref="segmentation_key"/>' + EOL)
    dimension_output_file.write(BLANK + '</dimension-column>' + EOL)
    export_mapping_index = 1
    d_mapping_export_mapping_index = 1
    for dimension_column in dimension_columns:
        WriteServiceModelDimensionColumn(dimension_output_file, dimension_column )
        export_mapping_index += 1
        d_mapping_export_mapping_index += 1
# ----------------------------------------------

def WriteServiceModelTail(dimension_output_file):
    tail = """</service>"""
    dimension_output_file.write(tail + EOL)
#----------------------------------------------

def WriteServiceModelMeasures(dimension_output_file, measures):
    dimension_output_file.write(EOL)
    for measure in measures:
        content = '<measure-column'
        for key , value in measure.attributes.items():
            if value != '':
                content += ' ' + key + '="' + value + '"'
        content += ' export-mapping="' + MEASURE__EXPOERT_MAPPING_PREFIX + str(MeasureItem.export_mapping_index) + '"'
        content += '>'
        dimension_output_file.write(BLANK + content + EOL)
        if measure.input_field != '':
            content = '<input-field ref="' + measure.input_field + '"/>'
            dimension_output_file.write(BLANK + BLANK + content + EOL)
        if measure.constant_value != '':
            content = '<constant value="' + measure.constant_value + '"/>'
            dimension_output_file.write(BLANK + BLANK + content + EOL)
        dimension_output_file.write(BLANK + '</measure-column>' + EOL)

        MeasureItem.export_mapping_index += 1
#----------------------------------------------

def WriteServiceModelCardinalities(dimension_output_file, dimension_columns):
    dimension_output_file.write(EOL)
    dimension_output_file.write(BLANK + '<column-cardinalities>' + EOL)
    dimension_output_file.write(BLANK + BLANK + '<column column-name="cal_timestamp_year" reserved="true"/>' + EOL)
    dimension_output_file.write(BLANK + BLANK + '<column column-name="cal_timestamp_quarter" reserved="true"/>' + EOL)
    dimension_output_file.write(BLANK + BLANK + '<column column-name="cal_timestamp_month" reserved="true"/>' + EOL)
    dimension_output_file.write(BLANK + BLANK + '<column column-name="cal_timestamp_week" reserved="true"/>' + EOL)
    dimension_output_file.write(BLANK + BLANK + '<column column-name="cal_timestamp_day" reserved="true"/>' + EOL)
    dimension_output_file.write(BLANK + BLANK + '<column column-name="cal_timestamp_hour" reserved="true"/>' + EOL)
    dimension_output_file.write(BLANK + BLANK + '<column column-name="cal_timestamp_time" reserved="true"/>' + EOL)

    for dimension in dimension_columns:
        dimension_output_file.write(BLANK + BLANK + '<column column-name="' + dimension.attributes[DIMENSION_COLUMN_NAME] + '"/>' + EOL)

    dimension_output_file.write(BLANK + '<column column-name="segmentation_key" segmentation-column="true"/>' + EOL)
    dimension_output_file.write(BLANK + '</column-cardinalities>' + EOL)
# ----------------------------------------------

def Process_ServerHeader(service_column, service_attr, service):
    CombineColumneAndValue(service_column, service_attr, service)
# ----------------------------------------------

def Process_Dimension(dimension_column, dimension_attr):
    dimension = DimensionItem()
    CombineColumneAndValue(dimension_column, dimension_attr, dimension)
    DimensionItem.dimensions.append(dimension)
    # load all dimension mapping columns
    if dimension.attributes['dimension mapping'] != '':
        d_mapping_item = DimensionMappingItem()
        d_mapping_item.dimension_mapping_name = dimension.attributes['dimension mapping']
        column_and_key = Pair()
        column_and_key.first = dimension.attributes[DIMENSION_COLUMN_NAME]
        column_and_key.second = dimension.attributes['dimension mapping key']
        d_mapping_item.dimension_mapping_items.append(column_and_key)
        DimensionMappingItem.dimension_mappings.append(d_mapping_item)
#----------------------------------------------

def Process_Measure(measure_column, measure_attr):
    measure = MeasureItem()
    CombineColumneAndValue(measure_column, measure_attr, measure)
    measure.attributes['column-name'] = measure.attributes[MEASURE_COLUMN_NAME]
    measure.attributes.pop(MEASURE_COLUMN_NAME)
    measure.input_field = measure.attributes['input field']
    measure.attributes.pop('input field')
    measure.constant_value = measure.attributes['constant value']
    measure.attributes.pop('constant value')
    MeasureItem.measures.append(measure)
# ----------------------------------------------

with open(CSV_FILE_PATH + CSV_FILE_NAME, 'r') as csv_input_file:
    with open(CSV_FILE_PATH + SERVICE_FILE_NAME, 'w') as service_output_file:
        lines = csv_input_file.readlines()
        for line in lines:
            columns =line.replace('\n', '').replace('\r', '').split(',')
            if str.lower(columns[0]) == SERVICE_MODEL_NAME:
                service_column = columns.copy()
                Current_Processing = PROCESS_SERVICEHEADER
                continue
            elif str.lower(columns[0]) == DIMENSION_COLUMN_NAME:
                dimension_column = columns.copy()
                Current_Processing = PROCESS_DIMENSION
                continue
            elif str.lower(columns[0]) == MEASURE_COLUMN_NAME:
                measure_column = columns.copy()
                Current_Processing = PROCESS_MESSURE
                continue

            if Current_Processing == PROCESS_SERVICEHEADER:
                service = ServiceBasicItem()
                Process_ServerHeader(service_column, columns.copy(), service)
            elif Current_Processing == PROCESS_DIMENSION:
                Process_Dimension(dimension_column, columns.copy())
            elif Current_Processing == PROCESS_MESSURE:
                Process_Measure(measure_column, columns.copy())

        WriteServiceModelHeader(service_output_file, service)
        WriteServiceModelDimensions(service_output_file, DimensionItem.dimensions)
        WriteServiceModelMeasures(service_output_file, MeasureItem.measures)
        WriteServiceModelCardinalities(service_output_file, DimensionItem.dimensions)
        WriteServiceModelTail(service_output_file)

print('Service model generated successfully!!!')