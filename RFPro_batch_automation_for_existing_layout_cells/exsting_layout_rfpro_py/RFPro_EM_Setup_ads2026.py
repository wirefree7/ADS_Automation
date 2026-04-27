def rfpro_sim_setup(Num_layout,wrk_name,lib,cells,HOME):
    import os

    try:
        import empro
        import empro.toolkit
        import empro.toolkit.analysis
        from empro.toolkit import touchstone, portparam
    except ImportError:
        print('Cannot import empro module')
        raise

    import keysight.edatoolbox.xxpro as xxpro
    import keysight.edatoolbox.ads as ads
    wrk_space_path=os.path.join(HOME,wrk_name)
    cell_sim=cells
    
    for i in range(1,Num_layout+1):
        cell=cell_sim[i-1]
        pro_lcv=ads.LibraryCellView(library=lib,cell=cell,view="rfprosetup")

        print("Creating RFPro Sim Setup for ",cell)

        xxpro.use_workspace(wrk_space_path)
        xxpro.load_pro_view(pro_lcv)
        empro.activeProject.saveActiveProject()
        # create an analysis
        with empro.activeProject as project:
            for component in empro.activeProject.layout.components:
                component.cellRole = empro.geometry.Component.LAYOUT
            empro.activeProject.layout.reExtractNets()
            empro.activeProject.saveActiveProject()
        #print(f'Component Roles done for {pro_lcv}...')
        # Create an Analysis
        analysis = empro.analysis.Analysis()
        analysis.name = f'EM_Setup_From_Python_for_{cell}'
        analysis.analysisType = empro.analysis.Analysis.EMFUAnalysisType
 
        # Set PortList
        portList1 = analysis.ports
        for pin_name1 in ['P1']:
            plusPins = [pin_name1]
            minusPins = ['P3']#, 'P5']#['Reference Pin On Cover']
            port = empro.toolkit.analysis.createPortFromPins(plusPins,minusPins)
            port.name = pin_name1
            port.referenceImpedance = empro.core.Expression(50.0)
            port.feedType = 'Auto' #'TML'
            port.referenceOffset = empro.core.Expression('3 mm')
            portList1.append(port)
            
        portList2 = analysis.ports
        for pin_name2 in ['P2']:
            plusPins = [pin_name2]
            minusPins = ['P4']#, 'P6']#['Reference Pin On Cover']
            port = empro.toolkit.analysis.createPortFromPins(plusPins,minusPins)
            port.name = pin_name2
            port.referenceImpedance = empro.core.Expression(50.0)
            port.feedType = 'Auto' #'TML'
            port.referenceOffset = empro.core.Expression('3 mm')
            portList2.append(port)   
            
            

        # Set Analysis Options
        options = analysis.simulationSettings
        # Set Ambient Conditions
        options.ambientConditions.backgroundTemperature = empro.core.Expression(298.15)

        # Set Frequency Plan List
        frequencyPlanList = options.femFrequencyPlanList()
        frequencyPlanList.clear()
        try:
            frequencyPlanList._frequencyPlanType = 'Interpolating_AllFields'
        except:
            print("New frequencyplan features are not available prior to 2023.20")
            pass

        plan = empro.simulation.FrequencyPlan()
        try:
            plan.computeType = 'Simulated'
            plan.sweepType = 'Adaptive'      
            plan.nearFieldType = 'NoNearFields'
            plan.farFieldType = 'NoFarFields'
        except:
            plan.type = 'Adaptive'  
            plan.enabled = True
        plan.startFrequency = empro.core.Expression('0 Hz')
        plan.stopFrequency = empro.core.Expression('10 GHz')
        plan.numberOfFrequencyPoints = 13 # 300 orginal value %%%%%%%%%%%%%%%%%%%
        plan.samplePointsLimit = 13 # 300 orginal value %%%%%%%%%%%%%%%
        plan.pointsPerDecade = 5
        frequencyPlanList.append(plan)

        # Set frequency plan global settings
        options.saveFieldsFor = 'AsDefinedByFrequencyPlans'
        options.farFieldEnabled = False
        options.farFieldAngularResolution = empro.core.Expression('5 deg')
        options.adaptiveFpMaxSamples = 13 # original value 300 %%%%%%%%%%%%%%%%%%%
        options.adaptiveFpSaveFieldsFor = 'AllFrequencies'

        # Set Simulator
        # Set Preset Simulator Setup By Name
        
        options.setPresetByName('Momentum RF')
        #options.setPresetByName('Momentum Microwave')
        #options.setPresetByName('FEM')

        # Set MoM Mesh Settings
        momMeshSettings = options.momMeshSettings
        momMeshSettings.meshGranularity = empro.core.Expression('10 cpw')
        momMeshSettings.edgeMesh = 'Off'

        # Set Resources Settings
        resourceSettings = empro.simulation.LocalResourceSettings()
        resourceSettings.numberOfWorkers = 1
        resourceSettings.numberOfThreads = 0
        options.resourceSettings = resourceSettings
        # Set ParameterSweep
        options.parameterSweepEnabled = False
        options.parameterSequences.clear()

        empro.activeProject.analyses.append(analysis)
        empro.activeProject.saveActiveProject()
        active_analysis = empro.activeProject.analyses[-1]
        empro.gui.processEvents()
        empro.toolkit.analysis.runAnalysis(active_analysis)

        print(f'Running and waiting for simulation {cell}...')
        empro.activeProject.simulations.isQueueHeld = False
        sim_from_list = empro.activeProject.simulations[-1]
        empro.toolkit.simulation.wait(sim_from_list)

        # Export Results in Touchstone & CSV formats

        res=empro.analysis.CircuitResults(active_analysis)
        ts_filename=os.path.join(wrk_space_path,'data',f"RFPro_result_{lib}_{cell}.s2p")
        res.write(ts_filename,"touchstone",17)
        print(f'Touchstone file written for {lib}_{cell}...')
        print(f'Simulation {lib}_{cell} Completed...')
        # source_file=ts_filename
        # dest_file=os.path.join(wrk_space_path,'data')
        import numpy as np
        freqs = list(res.frequencies())
        freqs = [f/1e9 for f in freqs]
        S11_dB = 20*np.log10(res.Src(0,0,"ComplexMagnitude"))
        S21_dB = 20*np.log10(res.Src(1,0,"ComplexMagnitude"))
        S12_dB = 20*np.log10(res.Src(0,1,"ComplexMagnitude"))
        S22_dB = 20*np.log10(res.Src(1,1,"ComplexMagnitude"))
        
        #S21_dB = 20*np.log10(S21_mag)
        
        S11_phase = res.Src(0,0,"Phase")
        S21_phase = res.Src(1,0,"Phase")
        S12_phase = res.Src(0,1,"Phase")
        S22_phase = res.Src(1,1,"Phase")

        csv_location=os.path.join(wrk_space_path,'data')
        output_file = os.path.join(csv_location,f"sparams_result_{lib}_{cell}.csv")
        with open(output_file,"w") as file:
            print(f"Writing CSV file for {lib}_{cell}...")
            line = ",".join(["Frequency", "S11 (dB)","S11 (phase)","S21 (dB)", "S21 (phase)","S12 (dB)", "S12 (phase)","S22 (dB)", "S22 (phase)"])
            file.write(line + "\n")
            for i in range(len(freqs)):
                line = f"{freqs[i]},{S11_dB[i]},{S11_phase[i]},{S21_dB[i]},{S21_phase[i]},{S12_dB[i]},{S12_phase[i]},{S22_dB[i]},{S22_phase[i]}"
                file.write(line + "\n")
        
        print(f"CSV files for all simulations can be found in: ",csv_location)

        empro.activeProject.clear()


