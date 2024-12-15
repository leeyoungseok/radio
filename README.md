# Radio segmentation and transcription
radio data segmentation and transcription project

0. directory, file name
mbc -> baechulsu -> 20241031 -> mp3/20241031.mp3
                                                  --> output/output-20241031/mbc-20241031.csv, 20241031-noenergy2.csv
                                                  --> transcript/output-20241031-transcript/segments_info.csv

1. mp3 file -> speech/music segmentation -> *.csv file
python ina-script.py --input_mp3_dir mp3_dir_name --output_dir output_dir_name
(ina-script는 별도 가상환경 설치 필요 tensorflow version이 별도로 필요함)
- mp3 파일 1개를 입력을 받아서, speech or music 으로 분류하여 csv 파일로 출력함
- mp3_dir_name: mbc
- output_dir_name: mbc-output

2. merge noenergy row from csv file
python merge-remove-noenergy2.py output_dir_name
- 1의 csv 파일 중 공백시간(noEnergy) 구간을 없앰
- output_dir_name: mbc-output

3. change mp3 file name
python mbc-filename-change.py
- filename은 날짜로
- mbc-2410312000.mp3 -> 20241031.mp3

4. change output dir/csv name
 python mbc-output-dir-filename-change.py
- mbc-output/output-24103120 -> mbc-output/output-20241031
- mbc-output/output-241031/24103120-noenergy2.csv -> mbc-output/output-20241031-noenery2.csv

5. python run-mp3-segmentation-3.py.  (ffmpeg + whisper)
- mp3 파일을 whisper로 받아쓰기(전사, transcription)함. 2의 결과 speech 만 할 수도 있음. music이 간혹 오류(speech -> music)가 날 수 있으니 music도 전사시킴
python run-mp3-segmentation-3.py --mp3_file_dir mbc --output_base_dir mbc-output --transcript_base_dir mbc-transcript

7. 음악 구간 탐지: input: segmented.csv (ina_speech_segmenter.py)
- 음악 구간(조각을 모으는 것)을 찾는 작업
python segment-1min-analyzer.py.   # 1분단위 음악, 음성 비율 계산하기, 70% 이상이면 csv file에 'Candidate' 컬럼에 song 추가하기
python segment-1min-music-revision.py  # segmented csv 파일에 'Revision"에 speech or music 보정하기

9. 광고 구간 탐지: input: segments_info.csv file, segmented.csv files
- 광고 구간을 탐지하는 작업
python csv-merge.py  # 입력 파일 2개: segments_info.csv + 1분 음악 탐지 결과 segmented.csv file  no, Candidate column 추가), 출력: new csv file (mbc-result.csv)
python radio-openai-ad.py.  # segments_info.csv (no, Candidate column 추가된) 의 transcript를 광고/음악   (10 second 단위)
python openai-10sec-ad-extraction.py  # 위의 광고 분류 결과를 추출하는 작업

11. openai's api summary
- 음악이 아닌 구간 (DJ 멘트)에 대한 요약을 생성
python radio-openai-summary-folder.py # 누적 100초 단위 그룹화로 텍스트 요약 생성
-> input: segmentes_file.csv
--> output: summary-date.txt file

13. txt -> html
- 웹 페이지 생성
python generate-html.py
python generate-index.py

15. To-do-list
- 텍스트 정확도 개선 -> 프롬프트? 파인튜닝? 선곡표 이용 방법?
  * 음악 제목
  * 가수 이름
  * 광고 이름
- Spotify 음악 재생 기능
-
