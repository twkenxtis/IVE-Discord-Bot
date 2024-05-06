import os
import json

def list_all_json_files():
    json_files = []
    for file in os.listdir('.'):
        if file.endswith(".json"):
            json_files.append((os.path.basename(file), len(json_files)+1))
    return sorted(json_files, key=lambda x: x[1])

# List all JSON files and let user choose one by index
print("Available JSON Files:")
for idx, filename in list_all_json_files():
    print(f"{filename}. {idx}")

while True:
    selected_idx = input("\nPlease enter the index of the desired JSON file: ")
    try:
        selected_idx = int(selected_idx)
        target_filename = next((fn for fn, idx in list_all_json_files() if idx == selected_idx), None)

        if target_filename:
            break
        else:
            print("\033[93mInvalid selection, please try again.\033[0m")
    except ValueError:
        print("\033[93mInvalid input, please enter a number.\033[0m")

if not target_filename:
    print("Invalid selection, exiting...")
else:
    print(f"You chose \033[38;5;118m{target_filename}\033[0m")
    
print ('Dict file content: \n')
# Read the chosen JSON file and process its content
with open(target_filename, "r") as d:
    posts_data = json.load(d)


if target_filename == 'Twitter_dict.json':
    for key, entry in posts_data.items():
        account, link, title, create_time, system_time,  tweet_post_time, num_images,  = entry
        
        print(f"\033[90mDictionary Entry: \033[0m\033[93m{key}\033[0m:\033[38;5;218m{entry} \033[0m \n")
        print(f"\033[90mKey: \033[0m\033[93m{key}\033[0m")
        print(f"\033[90mTwitter Account: \033[0m\033[38;2;255;102;102m{account}\033[0m")
        print(f"\033[90mLink: \033[0m\033[38;5;69m{link}\033[0m")
        print(f"\033[90mPost Title: \033[0m{title.encode('utf-8', 'replace').decode()} \033[90m|EndLine\033[0m")
        print(f"\033[90mTweet post time: \033[0m\033[38;5;99m{create_time}\033[0m")
        print(f"\033[90mTweet photo link:  \033[0m\033[38;5;218m{num_images}\033[0m")
        print(f"\033[90mNumber of tweet images \033[0m\033[38;5;118m{tweet_post_time}\033[0m")
        print(f"\033[90mcurrent system time: \033[38;5;21;\033{system_time}\033[0m")
        print('──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────')
else:
    for key, entry in posts_data.items():
        account, link, title, create_time, num_images,  system_time = entry
        
        print(f"\033[90mDictionary Entry: \033[0m\033[93m{key}\033[0m:\033[38;5;218m{entry} \033[0m \n")
        print(f"\033[90mKey: \033[0m\033[93m{key}\033[0m")
        print(f"\033[90mIG Account: \033[0m\033[38;2;255;102;102m{account}\033[0m")
        print(f"\033[90mLink: \033[0m\033[38;5;69m{link}\033[0m")
        print(f"\033[90mPost Title: \033[0m{title.encode('utf-8', 'replace').decode()} \033[90m|EndLine\033[0m")
        print(f"\033[90mPost create Time: \033[0m\033[38;5;99m{create_time}\033[0m")
        print(f"\033[90mNumber of IG images: \033[0m\033[38;5;118m{num_images}\033[0m")
        print(f"\033[90mcurrent system time: \033[38;5;21;\033{system_time}\033[0m")
        print('──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────')
