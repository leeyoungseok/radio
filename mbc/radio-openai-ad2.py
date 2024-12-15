import csv
import re
import argparse
from openai import OpenAI
from itertools import tee


# OpenAI API 키 설정
client = OpenAI(api_key=' ') 

def clean_transcript(transcript):
    # [] 부분 삭제
    transcript = re.sub(r'구독과\s*좋아요 부탁드려요!','', transcript)
    transcript = re.sub(r'구독과\s*좋아요','', transcript)

    return re.sub(r'\[.*?\]', '', transcript).strip()

def summary_request(transcript):
    clean_text = clean_transcript(transcript)

    # OpenAI API를 이용해 노래 가사인지 확인
    prompt = f"""
    다음 텍스트 내용을 읽고, [광고/광고아님/분류가 안됨] 3가지 중의 하나로 분류해주기 바랍니다.
    광고는 특정 제품에 대한 설명이 포함됩니다.
    광고로 분류되면 분류:광고
    광고 아니면 분류:아님
    분류가 안되면 분류:안됨
    이렇게 출력을 합니다.
    광고는 간단하게 제품, 회사 이름을 출력합니다.
    - 분류: 광고/아님/안됨
    - 제품:
    - 회사:
    
    텍스트:
    {clean_text}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,  # 응답의 최대 길이
        temperature=0.5,  # 창의성과 일관성의 균형
        n=1
    )

    result = response.choices[0].message.content.strip()
    return result

def clean_summary(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8-sig') as csvfile, open(output_file, 'w', encoding='utf-8-sig', newline='') as outfile:
        reader = csv.DictReader(csvfile)
        reader1, reader2 = tee(reader)  # 두 개의 반복자 생성
        next(reader2, None)  # reader2는 reader1보다 한 행 앞으로 이동

        fieldnames = reader.fieldnames + ["Summary"]  # Summary 컬럼 추가
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()  # 헤더 작성

        current_duration = 0
        combined_transcript = ""
        seg_start = 0
        seg_stop = 0
        current_type = []
        duration_list = []
        start_list = []
        mp3_list = []
        file_list = []

        for row, next_row in zip(reader1, reader2):
            duration = float(row['Duration'])
            transcript = row['Transcript']
            start = row['Start Time']
            stop = row['Stop Time']
            type = row['Type']
            mp3_name = row['MP3 File']
            file_name = row['Transcript File']

            clean_text = clean_transcript(transcript)
            combined_transcript += " / " + clean_text
            current_duration += duration
            seg_stop = stop
            current_type.append(type)
            duration_list.append(duration)
            start_list.append(start)
            mp3_list.append(mp3_name)
            file_list.append(file_name)

            next_duration = float(next_row['Duration'])

            if (current_duration > 5 and len(combined_transcript) > 5 ) or (next_duration > 5) :
                summary = summary_request(combined_transcript)
                #summary = "test"
                temp_duration = round(float(seg_stop) - float(seg_start), 1)
                writer.writerow({
                    "Start Time": round(float(seg_start), 1),
                    "Stop Time": round(float(seg_stop), 1),
                    "Duration": round(temp_duration, 1),
                    "Type": "; ".join(set(current_type)),
                    "MP3 File": "; ".join(set(mp3_list)),
                    "Transcript File": "; ".join(set(file_list)),
                    "Transcript": combined_transcript.strip(),
                    "Summary": summary
                })
                #writer.writerow(row)  # 결과 쓰기 
                #outfile.write(f"[{seg_start} : {seg_stop}] {minute}분 {seconds}초\n")
                combined_transcript = ""
                current_duration = 0
                current_type = []
                duration_list = []
                seg_start = seg_stop
                start_list = []
                mp3_list = []
                file_list = []

        # 마지막 누적된 텍스트 처리
        if combined_transcript:
            summary = summary_request(combined_transcript)
            row["Summary"] = summary
            writer.writerow(row)

    print(f"분석 결과가 {output_file}에 저장되었습니다.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a CSV file to classify and summarize transcript content.")
    parser.add_argument("input_file", help="Input CSV file path")
    parser.add_argument("output_file", help="Output CSV file path")
    args = parser.parse_args()

    clean_summary(args.input_file, args.output_file)
