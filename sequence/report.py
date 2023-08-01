def extract_and_write(input_file, output_file, start_line, end_line=float('inf')):
    try:
        with open(input_file, 'r') as infile, open(output_file, 'a') as outfile:
            lines = infile.readlines()
            start_line_index = max(0, start_line - 1)
            end_line_index = min(len(lines), end_line)

            extracted_lines = lines[start_line_index:end_line_index]
            outfile.writelines(extracted_lines)
            print(f"{len(extracted_lines)}行が {output_file} に書き込まれました。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

def add_text_to_last_line(input_file, output_file, text_to_add):
    try:
        with open(input_file, 'r') as infile:
            lines = infile.readlines()

        with open(output_file, 'a') as outfile:
            # 元のファイルの内容を新しいファイルに書き込む
            outfile.writelines(lines)

            # 「あいうえお」を追加して新しいファイルに書き込む
            outfile.write(text_to_add + '\n')

        print(f"「{text_to_add}」が {output_file} の最下行に追加されました。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")



#入力、出力するファイルを指定
input_file = 'C:/Users/arass/OneDrive/ドキュメント/GitHub/cansat2023/kari/cansat2023/sequence/log/phaselog0109.txt'
output_file = 'C:/Users/arass/OneDrive/ドキュメント/GitHub/cansat2023/kari/cansat2023/sequence/control_record_report.txt'
#使用例：抽出する行の範囲を3行目からファイルの最後までに指定
start_line = 3
extract_and_write(input_file, output_file, start_line)
print("1")

# 使用例：元のファイルの内容を読み込み、最下行に文章を追加して新しいファイルとして保存する
text_to_add = "Time and position at which the control ended:"
add_text_to_last_line(input_file, output_file, text_to_add)
print("2")
