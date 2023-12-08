# Define herd class
from simoolator.cow import Cow

class Herd:
    def __init__(self, outputs):
        self.list_of_cows = []
        self.outputs = outputs 

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
                       prev_output,
                       output_file,
                       filepath,
                       filename,
                       fileextension
                    ):
        print("Begin executing models...")
        for cow in self.list_of_cows:
            cow.execute_runModel(
                                Start,
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
    
    def import_dataframe(self, df):
        for index, row in df.iterrows():
            cow_variable = row['cow_ID']
            # print(cow_variable)
            cow_variable = Cow(name=row['name'], 
                               iStateVars=row['iStateVars'],
                               parameters=row['parameters'],
                               outputs=self.outputs)
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
   