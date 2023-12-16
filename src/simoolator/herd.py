# Define herd class
from simoolator.cow import Cow

class Herd:
    def __init__(self, outputs, model_functions, scenario_dict):
        self.list_of_cows = []
        self.outputs = outputs 
        self.model_functions = model_functions
        self.scenario_dict = scenario_dict

    def add_cow(self, cow):
        self.list_of_cows.append(cow)        

    def rollcall(self):
        for cow in self.list_of_cows:
            cow.moo()
        print(f"There are {Cow.total_cows} cows in the herd!")
        return 
    
    def run_all_models(self,
                       Start,
                       runTime,
                       integInt,
                       communInt,
                       model_index,
                       prev_output=None,
                        output_file=False,
                        filepath='./',
                        filename='generic',
                        fileextension='.csv'
                    ):
        print("Begin executing models...")
        for cow in self.list_of_cows:
            cow.execute_runModel(Start,
                                runTime,
                                integInt,
                                communInt,
                                model_index,
                                prev_output,
                                output_file,
                                filepath,
                                filename,
                                fileextension
            )
        print("Finished")
        return
    
    def run_all_scenarios(self,
                          Start,
                        runTime,
                        integInt,
                        communInt,
                        model_index,
                        prev_output=None,
                        output_file=False,
                        filepath='./',
                        filename='generic',
                        fileextension='.csv'):
        for cow in self.list_of_cows:
            for key, value in self.scenario_dict.items():
            # Eventually create a Scenario object with a method to pass variables this way
                scenario_param_name = key
                scenario_param_value = value

                cow.execute_runModel(Start, 
                                    runTime,
                                    integInt,
                                    communInt,
                                    model_index,
                                    scenario_param=scenario_param_value,
                                    prev_output=None,
                                    output_file=False,
                                    filepath='./',
                                    filename='generic',
                                    fileextension='.csv')
                print(f"Finished cow {cow.name} with {scenario_param_name}={scenario_param_value}")
        print("Finished all cows")
        return
    
    def import_dataframe(self, df):
        for index, row in df.iterrows():
            cow_variable = row['cow_ID']
  
            cow_variable = Cow(name=row['cow_ID'], 
                               iStateVars=row['iStateVars'],
                               parameters=row['parameters'],
                               outputs=self.outputs,
                               model_functions=self.model_functions)
            self.add_cow(cow_variable)
        print("All cows have been added")
        return
    
    def get_cow_by_id(self, cow_id):
        for cow in self.list_of_cows:
            if cow.name == cow_id:
                print("Cow found")
                return cow
        print("Cow not found")
        return 
   