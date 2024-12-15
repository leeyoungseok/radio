import csv
import re
import os
from openai import OpenAI
from datetime import datetime

# OpenAI API 키 설정
client = OpenAI(api_key=' ')

def clean_transcript(transcript):
    """Remove text in square brackets and trim whitespace."""
    return re.sub(r'\[.*?\]', '', transcript).strip()

def summary_request(transcript):
    """Send a request to the OpenAI API to summarize the transcript."""
    clean_text = clean_transcript(transcript)

    # Prompt for OpenAI
    prompt = f"""
    다음 텍스트 내용을 요약해주기 바랍니다.
    제목, 주요 내용, 청취자 사연(전화번호 또는 도시 또는 동 이름과 청취자 이름 그리고 청취자의 간단한 이야기), 음악 소개(제목, 가수 정보), 그리고 광고정보를 포함해주기 바랍니다.
    청취자 사연이 있을 수도 있고, 없을 수도 있습니다.
    음악 소개가 있을 수도 있고, 없을 수도 있습니다.
    음악 소개가 있으면, 제목과 가수 또는 연주악기 등에 대한 소개가 나옵니다.
    음악 제목이나 가수에 대한 설명이 영어, 스페이언어, 포루투갈어, 이탈리아어, 프랑스어 등이 원래 언어인데,
    한글로 받아쓰기해서 오류가 있을 수 있습니다. 오류가 있으면 수정해서 작성해야합니다.
    음악 소개가 있으면 보통 1곡이지만, 2곡 또는 연속적으로 3곡을 소개해줄 수도 있습니다.
    광고 정보도 있을 수도 있고, 없을 수도 있습니다.
    광고 정보는 간단하게 제품, 회사, 특징 정도만 요약해주면 됩니다.
    그리고 유튜브에서 나오는 텍스트는 처리하지 마세요. 예를 들어 구독과 좋아요같은 것은 오류입니다.
    이 라디오 프로그램은 MBC 방송국에서 진행되는 것이고, 진행자는 배철수입니다. 라디오 프로그램 이름은 배철수의 음악캠프입니다. 제목은 주요 내용, 사연, 음악 등에서 뽑아서 정해주어야합니다. 배철수의 음악캠프는 프로그램 제목이기때문에 텍스트 요약의 제목으로는 사용하지 않습니다. 광고내용이 제목으로 들어가서도 안됩니다.

    텍스트:
    {clean_text}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        temperature=0.5,
        n=1
    )

    return response.choices[0].message.content.strip()

def process_today_file(input_directory):
    """Process today's transcript file."""
    # Get today's date in YYYYMMDD format
    #today_date = "20241205"
    today_date = datetime.now().strftime('%Y%m%d')

    # Traverse the directory structure
    for root, dirs, files in os.walk(input_directory):
        for file in files:
            # Process files matching today's date
            if file.startswith('seg') and file.endswith('.csv') and f'output-{today_date}-transcript' in root:
                csv_file_path = os.path.join(root, file)
                output_file_path = os.path.join(root, f'summary-{today_date}.txt')

                print(f"Processing {csv_file_path}...")

                with open(csv_file_path, 'r', encoding='utf-8-sig') as csvfile, open(output_file_path, 'w', encoding='utf-8') as outfile:
                    reader = csv.DictReader(csvfile)
                    combined_transcript = ""
                    current_duration = 0
                    seg_start = 0

                    for row in reader:
                        duration = float(row['Duration'])
                        transcript = row['Transcript']
                        start = row['Start Time']
                        stop = row['Stop Time']
                        seg_stop = stop

                        clean_text = clean_transcript(transcript)
                        combined_transcript += clean_text
                        current_duration += duration

                        if current_duration > 100 and len(combined_transcript) > 10:
                            summary = summary_request(combined_transcript)
                            minute = round(float(seg_stop) - float(seg_start)) // 60
                            seconds = round(float(seg_stop) - float(seg_start)) % 60
                            outfile.write(f"[{seg_start} : {seg_stop}] {minute}분 {seconds}초\n")
                            outfile.write(summary + "\n")
                            outfile.write("--------------------------------------------\n")
                            combined_transcript = ""
                            current_duration = 0
                            seg_start = seg_stop

                    # Process the remaining transcript
                    if combined_transcript:
                        summary = summary_request(combined_transcript)
                        outfile.write("Summary: " + summary + "\n")

                print(f"Summary saved to {output_file_path}")
                return  # Stop after processing one file

    print("No files found for today's date.")

# Main execution
if __name__ == "__main__":
    # Base input directory
    input_directory = '/home/yslee/radio/mbc/baechulsu'
    process_today_file(input_directory)
