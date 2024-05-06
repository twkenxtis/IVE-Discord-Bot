# API_match_Twitter_access的

# TODO: Development 如果 Twitter_API 完工Release可以刪除!
if __name__ == '__main__':
    # Development codes
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    DEV_PATH = os.path.join('../decode_printer.txt')

    output_is_tuple = TwitterAccountProcessor(
        str(DEV_PATH)).process_twitter_account()

    print(
        '\033[38;2;255;102;102mDevelopment This is match twitter account tuple output: \033[0m')

    if output_is_tuple is None:
        print(Error_Log_Handler.error_log())
        pass
    # output_is_tuple[0] is binary search bool
    elif output_is_tuple[0] is False:
        print(Error_Log_Handler.error_log())
        pass
    else:
        print(type(output_is_tuple))
        print(output_is_tuple)
##########################################################################################
    with open(DEV_PATH, 'r', encoding='UTF-8', errors='ignore') as f:
        entry_list = f.read()
        entry_list = TwitterEntry_Tag_Processor.match_twitter_entry(entry_list)

        print(
            '\033[38;2;255;102;102mDevelopment This is twitter entry output: \033[0m')

        if not entry_list is None:
            # 將 entry_list 中的第一個元素以空格分割成單詞列表，選取以 '#' 開頭的單詞，並將它們存儲在列表中
            hashtags = [h for h in entry_list[0].split() if h.startswith('#')]
            # 使用 search_with_hashmap() 類方法搜索關鍵詞
            TwitterEntry_Tag_Processor.search_with_hashmap(hashtags)
            print(
                '\033[38;2;255;102;102mDevelopment This is hashtags output: \033[0m')
            print(type(TwitterEntry_Tag_Processor.search_with_hashmap(hashtags)))
            print(TwitterEntry_Tag_Processor.search_with_hashmap(hashtags))
            print(type(entry_list))
            print(entry_list)
        else:
            print(Error_Log_Handler.tag_error())
            pass