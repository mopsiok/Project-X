import socketserver
from common import *

#####################################################################
#                       Main application
#####################################################################

def main():
    print(f"Project X data storage - manual repair.\n")
    dataStorage, dataCache = data_init()
    print_storage_info(dataCache.cache, 5)

    repaired = manual_storage_repair(dataCache.cache)

    print("\nRepaired data:")
    print_storage_info(repaired, 5)
    if confirm("Overwrite data storage?"):
        serialized = serialize_samples(repaired)
        dataStorage.clear_write_data(serialized)
        print("Data overwritten.")
    else:
        print("Aborting.")

# repair this shit here, depending on the problem
def manual_storage_repair(messages_list: list):
    repaired = []

    # for msg in messages_list:
    #     if get_sample_time(msg) != 0:
    #         repaired.append(msg)
    #     else:
    #         print(f"Removing: {msg}")

    return repaired

def confirm(prompt="Confirm", default=False):
    valid_responses = {"yes": True, "y": True, "no": False, "n": False}
    default_prompt = "[Y/n]" if default else "[y/N]"
    response = input(f"{prompt} {default_prompt}: ").lower().strip()
    return valid_responses.get(response, default)

if __name__ == "__main__":
    main()