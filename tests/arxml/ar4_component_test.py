import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import autosar
from tests.arxml.common import ARXMLTestClass
import unittest

def _create_packages(ws):
    package=ws.createPackage('DataTypes', role='DataType')
    package.createSubPackage('CompuMethods', role='CompuMethod')
    package.createSubPackage('DataConstrs', role='DataConstraint')
    package.createSubPackage('Units', role='Unit')
    package.createSubPackage('BaseTypes')
    package = ws.createPackage('Constants', role='Constant')
    package = ws.createPackage('ComponentTypes', role='ComponentType')
    package = ws.createPackage('PortInterfaces', role="PortInterface")

def _create_base_types(ws):
    basetypes = ws.find('/DataTypes/BaseTypes')
    basetypes.createSwBaseType('boolean', 1, 'BOOLEAN')
    basetypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
    basetypes.createSwBaseType('uint16', 16, nativeDeclaration='uint16')
    basetypes.createSwBaseType('uint32', 32, nativeDeclaration='uint32')
    basetypes.createSwBaseType('float32', 32, encoding='IEEE754')
    package = ws.find('DataTypes')
    package.createImplementationDataType('boolean', valueTable=['FALSE','TRUE'], baseTypeRef='/DataTypes/BaseTypes/boolean', typeEmitter='Platform_Type')
    package.createImplementationDataType('uint8', lowerLimit=0, upperLimit=255, baseTypeRef='/DataTypes/BaseTypes/uint8', typeEmitter='Platform_Type')
    package.createImplementationDataType('uint16', lowerLimit=0, upperLimit=65535, baseTypeRef='/DataTypes/BaseTypes/uint16', typeEmitter='Platform_Type')
    package.createImplementationDataType('uint32', lowerLimit=0, upperLimit=4294967295, baseTypeRef='/DataTypes/BaseTypes/uint32', typeEmitter='Platform_Type')
    package.createImplementationDataTypeRef('PushButtonStatus_T', '/DataTypes/uint8', valueTable=['PushButtonStatus_Neutral', 'PushButtonStatus_Pushed', 'PushButtonStatus_Error', 'PushButtonStatus_NotAvailable'])

def _create_test_elements(ws):
    package = ws.find('/Constants')
    package.createConstant('VehicleSpeed_IV', 'uint16', 65535)
    package.createConstant('EngineSpeed_IV', 'uint16', 65535)
    package.createConstant('LastCyclePushButtonStatus_IV', 'uint8', 0)
    package = ws.find('/PortInterfaces')
    package.createSenderReceiverInterface('VehicleSpeed_I', autosar.DataElement('VehicleSpeed', 'uint16'))
    package.createSenderReceiverInterface('EngineSpeed_I', autosar.DataElement('EngineSpeed', 'uint16'))
    package.createSenderReceiverInterface('PushButtonStatus_I', autosar.DataElement('PushButtonStatus', 'PushButtonStatus_T', isQueued=True))
    package.createNvDataInterface('LastCyclePushButtonStatus_NvI', autosar.DataElement('LastCyclePushButtonStatus', 'PushButtonStatus_T'))
    package.createNvDataInterface('RebootCount_NvI', autosar.DataElement('RebootCount', 'uint32'))
    portInterface=package.createClientServerInterface('FreeRunningTimer5ms_I', ['GetTime', 'IsTimerElapsed'])
    portInterface['GetTime'].createOutArgument('value', '/DataTypes/uint32')
    portInterface["IsTimerElapsed"].createInArgument("startTime", '/DataTypes/uint32')
    portInterface["IsTimerElapsed"].createInArgument("duration", '/DataTypes/uint32')
    portInterface["IsTimerElapsed"].createOutArgument("result", '/DataTypes/boolean')

def _init_ws(ws):
    _create_packages(ws)
    _create_base_types(ws)
    _create_test_elements(ws)

class ARXML4ComponentTest(ARXMLTestClass):

    def test_create_application_software_component(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/ComponentTypes')
        swc = package.createApplicationSoftwareComponent('MyApplication')
        swc.createRequirePort('VehicleSpeed', 'VehicleSpeed_I', initValueRef = 'VehicleSpeed_IV')
        swc.createRequirePort('FreeRunningTimer', 'FreeRunningTimer5ms_I')
        swc.behavior.createRunnable('Run', portAccess=['VehicleSpeed', 'FreeRunningTimer/GetTime', 'FreeRunningTimer/IsTimerElapsed'])
        swc.behavior.createTimerEvent('Run', 20) #execute the Run function every 20ms in all modes
        file_name = 'ar4_application_swc.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'component', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])

    def test_create_service_software_component(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/ComponentTypes')
        swc = package.createServiceComponent('MyService')
        swc.createRequirePort('VehicleSpeed', 'VehicleSpeed_I', initValueRef = 'VehicleSpeed_IV')
        file_name = 'ar4_service_swc.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'component', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])

    def test_create_cdd_software_component(self):
        ws1 = autosar.workspace(version="4.2.2")
        _init_ws(ws1)
        package = ws1.find('/ComponentTypes')
        swc1 = package.createComplexDeviceDriverComponent('MyService')
        swc1.createRequirePort('VehicleSpeed', 'VehicleSpeed_I', initValueRef = 'VehicleSpeed_IV')
        file_name = 'ar4_cdd_swc.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'component', file_name)
        self.save_and_check(ws1, expected_file, generated_file, ['/ComponentTypes'])
        ws2 = autosar.workspace(ws1.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        swc2 = ws2.find(swc1.ref)
        self.assertIsInstance(swc2, autosar.component.ComplexDeviceDriverComponent)

    def test_create_composition_component(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/ComponentTypes')
        swc = package.createCompositionComponent('MyComposition')
        swc.createRequirePort('VehicleSpeed', 'VehicleSpeed_I', initValueRef = 'VehicleSpeed_IV')
        file_name = 'ar4_composition_swc.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'component', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])
        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))

    def test_create_composition_component_with_one_inner_swc(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/ComponentTypes')
        inner_swc = package.createApplicationSoftwareComponent('MyApplication')
        inner_port = inner_swc.createRequirePort('VehicleSpeed', 'VehicleSpeed_I', initValueRef = 'VehicleSpeed_IV')
        inner_swc.createRequirePort('FreeRunningTimer', 'FreeRunningTimer5ms_I')
        outer_swc = package.createCompositionComponent('MyComposition')
        outer_swc.createRequirePort('VehicleSpeed', 'VehicleSpeed_I', initValueRef = 'VehicleSpeed_IV')
        outer_swc.createComponentPrototype(inner_swc.ref)

        outer_swc.createConnector('VehicleSpeed', 'MyApplication/VehicleSpeed')
        file_name = 'ar4_composition_with_one_inner_swc.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'component', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])
        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))


    def test_create_server_component(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/ComponentTypes')
        swc = package.createApplicationSoftwareComponent('FrtServer')
        swc.createProvidePort('FreeRunningTimer5ms', 'FreeRunningTimer5ms_I')
        swc.behavior.createRunnable('FrtServer_FreeRunningTimer5ms_GetTime')
        swc.behavior.createRunnable('FrtServer_FreeRunningTimer5ms_IsTimerElapsed')
        swc.behavior.createOperationInvokedEvent('FrtServer_FreeRunningTimer5ms_GetTime', 'FreeRunningTimer5ms/GetTime')
        swc.behavior.createOperationInvokedEvent('FrtServer_FreeRunningTimer5ms_IsTimerElapsed', 'FreeRunningTimer5ms/IsTimerElapsed')

        file_name = 'ar4_server_component.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'component', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])
        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))

    def test_create_swc_with_queued_sender_com_spec(self):

        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/ComponentTypes')
        swc = package.createApplicationSoftwareComponent('ButtonPressHandler')
        swc.createProvidePort('ButtonPressUp', 'PushButtonStatus_I')
        swc.createProvidePort('ButtonPressDown', 'PushButtonStatus_I')

        file_name = 'ar4_swc_with_queued_sender_com_spec.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'component', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])
        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))

    def test_create_swc_with_queued_receiver_com_spec(self):

        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/ComponentTypes')
        swc = package.createApplicationSoftwareComponent('ButtonPressListener')
        swc.createRequirePort('ButtonPressUp', 'PushButtonStatus_I', queueLength=10)
        swc.createRequirePort('ButtonPressDown', 'PushButtonStatus_I', queueLength=10)

        file_name = 'ar4_swc_with_queued_receiver_com_spec.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'component', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])
        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))

    def test_create_application_software_component_with_nvdata_ports(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/ComponentTypes')
        swc = package.createApplicationSoftwareComponent('ButtonPressListener')
        swc.createRequirePort('ButtonPressUp', 'PushButtonStatus_I', queueLength=10)
        swc.createRequirePort('ButtonPressDown', 'PushButtonStatus_I', queueLength=10)

        with self.assertRaises(autosar.base.InvalidInitValueRef) as cm:
            swc.createRequirePort('LastCyclePushButtonStatus_1_NvR', 'LastCyclePushButtonStatus_NvI', initValueRef = 'NotValidRef')
        msg, = cm.exception.args
        self.assertEqual(msg, 'NotValidRef')

        invalidInitValue = ws.find('/DataTypes').find('PushButtonStatus_T')

        with self.assertRaises(ValueError) as cm:
            swc.createRequirePort('LastCyclePushButtonStatus_1_NvR', 'LastCyclePushButtonStatus_NvI', initValue = invalidInitValue)

        swc.createRequirePort('LastCyclePushButtonStatus_1_NvR', 'LastCyclePushButtonStatus_NvI', initValueRef = 'LastCyclePushButtonStatus_IV')
        swc.createProvidePort('LastCyclePushButtonStatus_1_NvW', 'LastCyclePushButtonStatus_NvI', ramBlockInitValueRef = 'LastCyclePushButtonStatus_IV', romBlockInitValueRef = 'LastCyclePushButtonStatus_IV')
        initValue = ws.find('/Constants').find('LastCyclePushButtonStatus_IV')
        swc.createRequirePort('LastCyclePushButtonStatus_2_NvR', 'LastCyclePushButtonStatus_NvI', initValue = initValue.value)
        swc.createRequirePort('RebootCount_NvR', 'RebootCount_NvI', initValue = int(1))
        swc.createProvidePort('RebootCount_NvW', 'RebootCount_NvI', ramBlockInitValue = int(2), romBlockInitValue = int(3))
        swc.behavior.createRunnable('run', portAccess=['LastCyclePushButtonStatus_1_NvR/LastCyclePushButtonStatus', 'LastCyclePushButtonStatus_1_NvW/LastCyclePushButtonStatus'])
        swc.behavior.createTimingEvent('run', 20) #execute the run function every 20ms in all modes
        file_name_generated = 'ar4_swc_with_nvdata_ports_generated.arxml'
        file_name_expected = 'ar4_swc_with_nvdata_ports.arxml'
        generated_file = os.path.join(self.output_dir, file_name_generated)
        expected_file = os.path.join( 'expected_gen', 'component', file_name_expected)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])

    def test_load_and_save_application_software_component_with_nvdata_ports(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        file_name = 'ar4_swc_with_nvdata_ports.arxml'
        expected_file = os.path.join( 'expected_gen', 'component', file_name)
        expected_path = os.path.join(os.path.dirname(__file__), expected_file)
        generated_file = os.path.join(self.output_dir, file_name)
        ws.loadXML(expected_path)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])

    def test_create_nvblock_software_component(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/ComponentTypes')
        swc = package.createNvBlockComponent('NvBlockHandler')
        swc.createRequirePort('LastCyclePushButtonStatus_NvR', 'LastCyclePushButtonStatus_NvI')
        swc.createRequirePort('RebootCount_NvR', 'RebootCount_NvI')
        swc.behavior.createRunnable('run')
        Run_Event = swc.behavior.createTimingEvent('run', 20) #execute the run function every 20ms in all modes
        swc.behavior.createRunnable('NvBlockHandler_DataWrittenCallback')
        swc.behavior.createDataReceivedEvent('NvBlockHandler_DataWrittenCallback', 'RebootCount_NvR')

        nvmBlockConfig = autosar.behavior.NvmBlockConfig(numberOfDataSets=2,
                                        numberOfRomBlocks=1,
                                        ramBlockStatusControl='NV-RAM-MANAGER',
                                        readOnly=False,
                                        reliability='ERROR-DETECTION',
                                        resistantToChangedSw=True,
                                        restoreAtStartup=True,
                                        storeAtShutdown=True,
                                        storeImmediate=True,
                                        storeCyclic=False,
                                        storeEmergency=False,
                                        useCrcCompMechanism=True,
                                        writeOnlyOnce=False,
                                        writeVerification=True,
                                        writingFrequency=10000,
                                        writingPriority='LOW',
                                        checkStaticBlockId=False,
                                        autoValidationAtShutdown=False,
                                        cyclicWritePeriod=0)

        autosar.behavior.createNvBlockDescriptor(swc, 'LastCyclePushButtonStatus_NvR',
                NvmBlockConfig=nvmBlockConfig, timingEventRef=Run_Event.name, swCalibrationAccess='READ-WRITE', supportDirtyFlag=True,
                romBlockInitValueRef = 'LastCyclePushButtonStatus_IV', romBlockDesc="Rom block description", romBlockLongName="Rom block long name")

        file_name = 'ar4_nvblock_swc.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'component', file_name)
        expected_path = os.path.join(os.path.dirname(__file__), expected_file)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        ws.loadXML(expected_path)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])

    def test_create_application_software_component_with_invalid_ports(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/ComponentTypes')
        swc = package.createApplicationSoftwareComponent('InvalidInterfacesTest')
        VehicleSpeed = swc.createRequirePort('VehicleSpeed', 'VehicleSpeed_I')
        EngineSpeed = swc.createProvidePort('EngineSpeed', 'EngineSpeed_I')

        # Save and change the require ref
        VehicleSpeedPortInterfaceRef = VehicleSpeed.portInterfaceRef
        VehicleSpeed.portInterfaceRef = 'Invalid_ref_1'

        file_name = 'ar4_swc_with_invalid_ports.arxml'
        generated_file = os.path.join(os.path.dirname(__file__), self.output_dir, file_name)
        with self.assertRaises(autosar.base.InvalidPortInterfaceRef) as cm:
            ws.saveXML(generated_file, filters=['/ComponentTypes'])
        msg, = cm.exception.args
        self.assertEqual(msg, "/ComponentTypes/InvalidInterfacesTest/VehicleSpeed: Invalid_ref_1")

        # Restore and change the provide ref
        VehicleSpeed.portInterfaceRef = VehicleSpeedPortInterfaceRef
        EngineSpeed.portInterfaceRef = 'Invalid_ref_2'

        with self.assertRaises(autosar.base.InvalidPortInterfaceRef) as cm:
            ws.saveXML(generated_file, filters=['/ComponentTypes'])
        msg, = cm.exception.args
        self.assertEqual(msg, "/ComponentTypes/InvalidInterfacesTest/EngineSpeed: Invalid_ref_2")
        os.remove(generated_file)


if __name__ == '__main__':
    unittest.main()
