from fastapi import FastAPI 
from pydantic import BaseModel
from pathlib import Path
from openai import OpenAI
from pydub import AudioSegment
import os
from dotenv import load_dotenv
import boto3
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

AWS_API_KEY = os.environ["AWS_API_KEY"]
AWS_ACCESS_KEY_ID =os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_DEFAULT_REGION = os.environ["AWS_DEFAULT_REGION"]

app = FastAPI()

class Data_request(BaseModel):
	chatList: list
	userID: str
	roleplayID: str

@app.post("/video")
def makeVideo(data_requst: Data_request):
	try:
		voice_dic = {'woman': 'nova', 'man': 'echo', 'oldWoman': 'alloy', 'oldMan': 'onyx'}
		openAIclient = OpenAI(api_key=AWS_API_KEY)
		dynamodb = boto3.resource('dynamodb', 
					region_name=AWS_DEFAULT_REGION,
					aws_access_key_id=AWS_ACCESS_KEY_ID,
					aws_secret_access_key=AWS_SECRET_ACCESS_KEY
		)
		table = dynamodb.Table('LipRead')
		s3client = boto3.client('s3',
        		    aws_access_key_id=AWS_ACCESS_KEY_ID,
            		aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            		region_name=AWS_DEFAULT_REGION
    	)
		percentageAmount = 90 // len(data_requst.chatList)

		for idx, chat in enumerate(data_requst.chatList):
			#음성 생성
			speech_name_mp3 = str(data_requst.roleplayID)+"_"+str(idx)+".mp3"
			speech_file_path = Path(__file__).parent / speech_name_mp3
			response = openAIclient.audio.speech.create(
  				model="tts-1-hd",
  				voice=voice_dic[chat['roleType']],
  				input=chat['text']
			)
			response.stream_to_file(speech_file_path)
			#음성 변환 (mp3 -> wav)
			AudioSegment.from_mp3(speech_name_mp3).export(str(data_requst.roleplayID)+"_"+str(idx)+".wav", format="wav")

			#영상 생성
			source_video_path = "./"+chat['roleType']+".mp4"
			openface_landmark_path = "./"+chat['roleType']+".csv"
			driving_audio_path = "./"+str(data_requst.roleplayID)+"_"+str(idx)+".wav"
			result_name = str(data_requst.roleplayID)
			command = "python inference.py --mouth_region_size=256 --source_video_path="+ source_video_path +" --source_openface_landmark_path="+ openface_landmark_path +" --driving_audio_path="+ driving_audio_path +" --result_name="+ result_name+" --pretrained_clip_DINet_path=./asserts/clip_training_DINet_256mouth.pth"
			os.system(command)

			#영상 업로드
			file_name = "./asserts/inference_result/" + result_name + ".mp4"    # 업로드할 파일 이름 
			bucket = 'lip-reading-project-bucket'           	# 버켓 주소
			key = chat['videoUrl'][37:]	# s3 파일 이미지 이름-> roleplayID+순서
			s3client.upload_file(file_name, bucket, key) #파일 저장

			os.remove("/home/ubuntu/project/ML-Server/"+str(data_requst.roleplayID)+"_"+str(idx)+".mp3")
			os.remove("/home/ubuntu/project/ML-Server/"+str(data_requst.roleplayID)+"_"+str(idx)+".wav")
			os.remove("/home/ubuntu/project/ML-Server/asserts/inference_result/"+str(data_requst.roleplayID)+".mp4")	

			#데이터베이스 percentage 업데이트
			if idx+1 == len(data_requst.chatList):
				table.update_item(
    				Key={
        				'PK': data_requst.userID,
        				'SK': data_requst.roleplayID,
    				},
    				UpdateExpression='SET percentage = :percentage, #s = :status',
	    			ExpressionAttributeValues={
    	    			':percentage': 100,
						':status': "done"
    				},
					ExpressionAttributeNames={
						'#s':"status"
					}
				)
			else:
				table.update_item(
    				Key={
        				'PK': data_requst.userID,
        				'SK': data_requst.roleplayID,
	    			},
    				UpdateExpression='SET percentage = :percentage',
	    			ExpressionAttributeValues={
    	    			':percentage': percentageAmount*(idx+1) + 10
    				}
				)

		lambda_client = boto3.client('lambda',
                region_name=AWS_DEFAULT_REGION,
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
		)
		response = lambda_client.invoke(
    		FunctionName='lambda-pushAlarm-api',
    		InvocationType='Event',
    		Payload=json.dumps({ "userID": data_requst.userID, "roleplayID": data_requst.roleplayID })
		) 

		os.remove("./"+str(data_requst.roleplayID)+".mp3")
		os.remove("./"+str(data_requst.roleplayID)+".wav")
		os.remove("./asserts/inference_result/"+str(data_requst.roleplayID)+".mp4")
		
		return {
			"message": "영상 생성 성공",
			"success": True,
		}
	
	except Exception as e:
		return {
			"success": False,
			"message": str(e)
		}