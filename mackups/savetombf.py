import subprocess
import json
import os

#Create a file for backup before setup maybe
try:
    file_dictionary_json = json.load("r","macro_backup_config.json")
except:
    #to check if the default only runs when the json fails to run 
    fault_dictionary = {
        "included_folders":"/",
        "backup_format":"mbf",
        "dta_or_efi":"efi"
    }

def get_machine_info():
    try:
        subprocess.run("cat /etc/procinfo")
    except:
        try:
            subprocess.run("cat /etc/os-release")
        except:
            subprocess.run("cat /proc/cpuinfo")
#get the machine info so that you can put the information into a mbf file
    machine_spec = {
        "osname" : ""
    }
def compress_to_spec(included_folders, backup_format, dta_or_efi):
    if backup_format == "mbf":
        print("Smart Zipping")
        if dta_or_efi == "efi":
            print("Efi Zip")
        elif dta_or_efi == "dta":
            print("Dta Zip")
        else:
            print("Defaulting to efi")

    elif backup_format == "zip":
        print("dta_or_efi doesn't apply when using zip")
    else:
        print("No backup format specified. Defaulting to mbf")
