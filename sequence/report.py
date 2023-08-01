def extract_and_write(input_file, output_file, start_line, end_line=float('inf')):
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            lines = infile.readlines()
            start_line_index = max(0, start_line - 1)
            end_line_index = min(len(lines), end_line)

            extracted_lines = lines[start_line_index:end_line_index]
            outfile.writelines(extracted_lines)
            print(f"{len(extracted_lines)}行が {output_file} に書き込まれました。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# 使用例：抽出する行の範囲を3行目からファイルの最後までに指定
input_file = 'C:\Users\arass\OneDrive\ドキュメント\GitHub\cansat2023\kari\cansat2023\sequence\log\phaselog0109.txt'
print("1")
output_file = 'C:\Users\arass\OneDrive\ドキュメント\GitHub\cansat2023\kari\cansat2023\sequence\control_record_report.txt'
print("1")
start_line = 3
extract_and_write(input_file, output_file, start_line)
print("1")
