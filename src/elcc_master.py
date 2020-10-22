import sys
import os

from elcc_impl import main


# Parameters

simulation = dict()
files = dict()
system = dict()
generator = dict()

####################################### DEFAULT #############################################

########## Generic ##########

simulation["year"] = 2018
simulation["region"] = ["nyiso"] # identify the nerc region or balancing authority (e.g. "PACE", "WECC", etc.)
simulation["iterations"] = 10000 # number of iterations for monte carlo simulation
simulation["target reliability"] = 2.4 # loss-of-load-hours per year (2.4 is standard)
simulation["shift load"] = 0 # +/- hours
simulation["debug"] = False # print all information flagged for debug

######## files ########

files["output directory"] = "./"
files["eia folder"] = "../eia8602018/"
files["benchmark FORs file"] =  "../efor/Temperature_dependent_for_realtionships.xlsx"
files["total interchange folder"] = "../total_interchange/"
files["saved systems folder"] = "/scratch/mtcraig_root/mtcraig1/shared_data/elccJobs/savedSystems/"

########## System ########### 

# Adjust parameters of existing fleet
system["system setting"] = "save" # none or save (save will load existing fleet capacity or save new folder)
system["oldest year"] = 0 #remove conventional generators older than this year

######### Outages ###########

system["conventional efor"] = .05 #ignored if temperature-dependent FOR is true
system["renewable efor"] = .05 #set to 1 to ignore all W&S generators from current fleet
system["temperature dependent FOR"] = True #implemnts temeprature dependent forced outage rates for 6 known technologies
system["temperature dependent FOR indpendent of size"] = True #implemnts temperature dependent forced outage rates for all generators, 
                                                            #if false only applies to generators greater then 15 MW, ignore if not using temp dependent FORs
system["enable total interchange"] = True #gathers combined imports/exports data for balancing authority N/A for WECC

######### Storage ###########

system["dispatch strategy"] = "reliability" 
system["storage efficiency"] = .8 #roundtrip 
system["storage efor"] = 0
system["fleet storage"] = True #include existing fleet storage 
system["supplemental storage"] = False # add supplemental storage to simulate higher storage penetration
system["supplemental storage power capacity"] = 1000 # MW
system["supplemental storage energy capacity"] = 1000 # MWh

######## Generator ##########

generator["generator type"] = "solar" #solar or wind 
generator["nameplate"] = 1000 #MW
generator["latitude"] = 41
generator["longitude"] = -112
generator["efor"] = .05 

###### Added Storage ########

generator["generator storage"] = False #find elcc of additional storage
generator["generator storage power capacity"] = 1000 #MW
generator["generator storage energy capacity"] = 1000 #MWh 

##############################################################################################

redirect_output = len(sys.argv[1:]) % 2 == 1

# handle arguments depending on job based on key-value entries. for multi-word keys, use underscores.
#
#   e.g.        python elcc_master.py year 2017 region WECC print_debug False 
#

if redirect_output:
    root_directory = sys.argv[1]
    parameters = sys.argv[2:]

    if root_directory[-1] != '/': root_directory += '/'
    if not os.path.exists(root_directory):
        print('Invalid directory:', root_directory)
        sys.exit(1)

else:
    parameters = sys.argv[1:]

i = 0
while i < len(parameters):
    key = parameters[i].replace('_',' ')
    value = parameters[i+1]

    if key == "region":
        simulation['region'] = value.split()

    else:
        for param_set in [simulation, files, system, generator]:
            if key in param_set:

                param_set[key] = str(value)

                # handle numerical arguments
                try:
                    # floats
                    float_value = float(value)
                    param_set[key] = float_value
        
                    # ints
                    if float(value) == int(value):
                        param_set[key] = int(value)
                except:
                    pass

                # handle boolean arguments
                if value == "True": param_set[key] = True
                elif value == "False": param_set[key] = False
            
    i += 2 

# dependent parameters

files["solar cf file"] = "../wecc_powGen/"+str(simulation["year"])+"_solar_generation_cf.nc"
files["wind cf file"] = "../wecc_powGen/"+str(simulation["year"])+"_wind_generation_cf.nc"
files["temperature file"] = "../efor/temperatureDataset"+str(simulation["year"])+".nc"
files["eia folder"] = "../eia860"+str(simulation["year"])+"/"

# time savers

if simulation["region"] == ["WECC"]:
    system['enable total interchange'] = False
    system['oldest year'] = 1975


if files["output directory"][-1] != '/': files["output directory"] += '/'
if files["saved systems folder"][-1] != '/': files["saved systems folder"] += '/'

# handle output directory and print location

if redirect_output:

    output_directory = root_directory+"elcc.__"

    # default parameters
    if len(sys.argv) == 2:
        output_directory += "default.out"

    # handle all parameters
    else: 
        # add each passed parameter
        for parameter in sys.argv[1:]:
            if parameter.find('/') == -1: #don't include files/directories
                output_directory += parameter + "__"

        # add tag
        output_directory += ".out"
        output_directory.replace('/','.')

    # Error Handling
    if os.path.exists(output_directory):
        print("Duplicate folder encountered:",output_directory)
        sys.exit(1)

    # Create directory
    os.system("mkdir "+output_directory)

    output_directory += '/'

    sys.stdout = open(output_directory + 'print.out', 'w')
    sys.stderr = sys.stdout

    files['output directory'] = output_directory


# run program
main(simulation,files,system,generator)
