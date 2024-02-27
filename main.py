from fastapi import FastAPI 
from pydantic import BaseModel
from pathlib import Path
from openai import OpenAI
from pydub import AudioSegment
import os
from dotenv import load_dotenv
import boto3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

AWS_API_KEY = os.environ["AWS_API_KEY"]
AWS_ACCESS_KEY_ID =os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_DEFAULT_REGION = os.environ["AWS_DEFAULT_REGION"]

app = FastAPI()

class Data_request(BaseModel):
	chat: dict
	roleplayID: str


@app.post("/video")
def makeVideo(data_requst: Data_request):
	#음성 생성
	voice_dic = {'woman': 'nova', 'man': 'echo', 'oldWoman': 'alloy', 'oldMan': 'onyx'}
	client = OpenAI(api_key=AWS_API_KEY)
	speech_file_path = Path(__file__).parent / "speech.mp3"
	response = client.audio.speech.create(
  		model="tts-1-hd",
  		voice=voice_dic[data_requst.chat['roleType']],
  		input=data_requst.chat['text']
	)
	response.stream_to_file(speech_file_path)
	#음성 변환(mp3 -> wav)
	AudioSegment.from_mp3("speech.mp3").export("speech.wav", format="wav")

	#영상 생성
	source_video_path = "./woman.mp4"
	openface_landmark_path = "./woman.csv"
	driving_audio_path = "./speech.wav"
	command = "python inference.py --mouth_region_size=256 --source_video_path="+ source_video_path +" --source_openface_landmark_path="+ openface_landmark_path +" --driving_audio_path="+ driving_audio_path +" --pretrained_clip_DINet_path=./asserts/clip_training_DINet_256mouth.pth"
	os.system(command)

	#영상 업로드
	client = boto3.client('s3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_DEFAULT_REGION
    )

	file_name = './asserts/inference_result/woman_facial_dubbing_add_audio.mp4'     # 업로드할 파일 이름 
	bucket = 'lip-reading-project-bucket'           	# 버켓 주소
	key = data_requst.roleplayID + '_' + str(data_requst.chat['idx']) + '.mp4'	# s3 파일 이미지 -> roleplayID+순서
	client.upload_file(file_name, bucket, key) #파일 저장
	
	return {
		"video": key
	}