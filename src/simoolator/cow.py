# Define Cow class

class Cow:
    total_cows = 0

    def __init__(self, name, iStateVars, parameters, outputs):
        self.name = name
        self.iStateVars = iStateVars
        self.parameters = parameters
        self.results_dataframe = None
        self.outputs = outputs
        Cow.total_cows += 1

    def __repr__(self):
        return f"Cow({self.name})"

    def moo(self):
        num_o = min(max(len(self.name) % 8, 2), 8)
        moo_sound = 'M' + 'o' * num_o
        print(f"{self.name}: {moo_sound}")

    def laccurve5_dijkstra(self, stateVars, t, prev_var_return=None):
            # prev_var_return is required if you want to have a variable with an initial value that then gets updated each iteration
            # The variable must also be included in the outputs
            # TODO ask John about this issue, how common is it to have variables like this

        import numpy as np
        import math

        # Assign Parameter Values #
        a = self.parameters['a']
        b = self.parameters['b']
        b0 = self.parameters['b0']
        c = self.parameters['c']
        L = self.parameters['L']
        KDMIMILK = self.parameters['KDMIMILK']
        KDMImbw = self.parameters['KDMImbw']
        Hcfeed = self.parameters['Hcfeed']
        Hcmilk = self.parameters['Hcmilk']
        KL = self.parameters['KL']
        expL = self.parameters['expL']
        pregdate = self.parameters['pregdate']
        kf1 = self.parameters['kf1']
        kf2 = self.parameters['kf2']
        milk_value = self.parameters['milk_value']

        # Paramaters that require an initial value #
        if t == 0:
             E = self.parameters['E']
        else:
            E = prev_var_return[5]


        # Variables w/ Differential Equation #
        BW = stateVars[0]
        ER = stateVars[1]
        milkcumul = stateVars[2]
        DMIcumul = stateVars[3]
        IOFCcumul = stateVars[4]

        # Model Equations # 
        feed_price = (101 * Hcfeed + 2.7) / 1000

        BFat = ER/9.0       
        # Body fat
    
        Lmod = 1.0-(1.0-L)/(1.0+(KL/BFat)**expL)         
            # 1 - (1-L) = L?
            # Modifying value of L? Why the adjustment?

        dijkstra_milk = a * np.exp(b * (1 - np.exp(-b0 * t)) / b0 - c * t)
        # John has modified S to give 4% FCM yield per alveolus 

        NEmilk = E**Lmod*dijkstra_milk                         
            # Net energy milk
            # On slide 28 this is equation for FCM yield but L is modified here
            # Is L modified to give a NEmilk as well as a milk yield (milk)

        milk = NEmilk/Hcmilk                
            # Milk production

        DMINRC = (KDMIMILK * milk + KDMImbw * BW**0.75)*(1.0-math.exp(-0.192*(t/7+3.67)))   
            # Slide 28
            # NRC DMI equation

        fdbk = (kf1*t/7+kf2)*(ER-iER)/iER               
        # Ellis 2006
            # Feedback on DMI

        DMI = DMINRC - fdbk                             
            # Dry matter intake     

        NEI = Hcfeed*DMI                                
            # Net energy intake

        NEmaint = 0.096*BW**0.75                        
            # Net energy maintenance

        if t < pregdate + 190:                          
            NEgest = 0
        else:
            NEgest = (0.00318*(t-pregdate-190)-0.0352)/0.218
            # Net energy gestation

        NEreqt = NEmaint + dijkstra_milk + NEgest + 5.12*2.0          
            # NE requirement, from NRC

        E = NEI/NEreqt            
            # Energy balance

        # Differential Equations # 
        dERdt = NEI - NEmaint - NEmilk - NEgest
        # Energy requirement (NE)
    
        if dERdt < 0:
            dBWdt = dERdt/4.92  # 4.92 Mcal/kg in NRC(1988)
        else:
            dBWdt = dERdt/5.12  # 5.12 Mcal/kg for gain
            # Bodyweight gain

        IOFC = (milk * milk_value) - (DMI * feed_price)

        # Format data for return # 
        differential_return = [dBWdt, dERdt, milk, DMI, IOFC]
        local_variables = locals()
        # Store local variables 
        variable_returns = [local_variables.get(variable_name) for variable_name in self.outputs]
        # Create list of variables to return

        return differential_return, variable_returns

    def runModel(self, Start, runTime, integInt, communInt,
                 model_function,
                 prev_output=None,
                 output_file=False,
                 filepath='./',
                 filename='generic',
                 fileextension='.csv'):
        
        import pandas as pd
        from datetime import datetime

        ### Setup Integration and Communication Loop ###
        lastIntervalNo=runTime/integInt 
        intervalNoForComm=communInt/integInt
        cintAsInt=int(intervalNoForComm)

        ### Initialize Lists ###
        model_results = []  # Store model results, a list of lists
        slopes=[] # list to hold slopes (diff eqn results) for Runge-Kutta
        start=[] # list to hold stateVar values at beginning of current integInt
        
        print("Running Model....")

        ####################
        # Start New Simulation
        ####################
        if Start==0: # start from t=0 instead of continue from where it left off
            t=0.0 # start time for simulation
            # Run model at time=0, uses initial state variables that user input
            differential_return, variable_returns = model_function(stateVars=self.iStateVars,
                                                                #    prev_var_return=variable_returns,
                                                                   t=t)                                                             
            model_results.append(variable_returns)        
                # dynamic() now returns a list of variables that can be appended into model_results

        ####################
        # Continue Simulation
        ####################
        if Start == 1:
            # check that prev_output has been included
            if not isinstance(prev_output, pd.DataFrame):
                raise TypeError("The variable prev_output must be a dataframe if Start == 1")

        # 4th-order Runge Kutta algorithm to iterate through dynamic() between t = 0 and tStop
        stateVars = self.iStateVars.copy()
            # Create copy of the initial state variables 
        for intervalNo in range(int(lastIntervalNo)):
            for n in range(4): # 4 parts to Runge-Kutta estimation of new state
                # eval model fluxes and store diff eqn results in slopes[part][statevar] for 
                # each part of Runge-Kutta by calling dynamic() here:
                differential_return, variable_returns = model_function(stateVars=stateVars,
                                                                       prev_var_return=variable_returns,
                                                                       t=t)
                slopes.append(differential_return)  # Add list of differentials
                for svno in range(len(stateVars)): # estimate new stateVar values 1 at a time
                    match n:
                        case 0: # if part 1 of Runge-Kutta, record state at beginning of integInt
                            start.append(stateVars[svno]) # to be used throughout
                            newStateVar=start[svno]+integInt*slopes[n][svno]/2
                        case 1: # if part 2 of Runge Kutta
                            newStateVar=start[svno]+integInt*slopes[n][svno]/2
                        case 2: # if part 3 of Runge Kutta
                            newStateVar=start[svno]+integInt*slopes[n][svno]
                        case 3: # if part 4 of Runge-Kutta, use all 4 slopes to estimate new state
                            newStateVar=start[svno]+integInt/6*(slopes[0][svno]+2*slopes[1][svno]+
                                2*slopes[2][svno]+slopes[3][svno])
                            
                    stateVars[svno]=newStateVar 
                        # update stateVars w new values after each part of Runge-Kutta:
            # end of one iteration thru complete 4th-order Runge-Kutta algorithm = 1 integInt
            t+=integInt 
                # increment time to associate with new state
            # output results of new state if new time is a communication time
            # current intervalNo is associated with old time so intervalNo+1 is used
            remainder=(intervalNo+1)/cintAsInt-int((intervalNo+1)/cintAsInt)
            if remainder==0:
                model_results.append(variable_returns.copy()) # appends pointer to temp outputRow so need to append copy
            slopes.clear() # clear slopes list for next integInt
            start.clear() # clear temp list for next integInt

        ####################
        # Export Model Results
        ####################
        output_dataframe = pd.DataFrame(model_results, columns=self.outputs)

        if Start == 1:
            # join new data onto previous data
            output_dataframe = pd.concat([prev_output,output_dataframe], ignore_index=True)

        if output_file == True:
            # get current date/time as string
            timestamp = datetime.datetime.now().strftime('%y%m%d_%H%M%S') 
            
            # put together full filename and path
            full_filename = filepath + filename + timestamp + fileextension
            print("File saved to: " + full_filename)

            # save to csv
            output_dataframe.to_csv(full_filename, index=False)
        
        print(output_dataframe)

        print("Running Model....DONE")

        # return the dataframe to be used later
        return output_dataframe

    def execute_runModel(self):
        # Call the runModel method
        self.results_dataframe = self.runModel(0,
                                               307,
                                               0.001,
                                               7,
                                            #    outputs_list=self.outputs,
                                            #    parameters=self.parameters,
                                            #    initital_stateVars=self.iStateVars,
                                               model_function=self.laccurve5_dijkstra
                                               )

    def get_cow_parameters(self):
        cow_data = [self.name, self.parameters, self.iStateVars, self.results_dataframe]
        return cow_data
