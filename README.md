# LipRead - ML Server    
## 🦻🏻 프로젝트 소개
> 청각장애인을 위한 구어 학습 서비스

청각 장애인들이 실생활에서 자주 쓰이는 문장을 중심으로 구어를 학습할 수 있는 서비스 입니다.   
LipRead는 AI를 통해 제작된 대화 영상을 통해 청각장애인들의 독화 훈련과 청능 훈련을 도와 다양한 상황에서 의사소통을 원활히 할 수 있도록 도움을 주고자 합니다. 

LipRead PPT (https://github.com/sookmyung-graduation-project-2023/Server/blob/main/PPT.md)  
<br/>  

## 📚개발 기간
2023.11.2 ~ 2024.03.19 

[Yun JaeEun](https://github.com/yunjaeeun44) : Back-end Developer  
[Lee YuJin](https://github.com/Ujaa) : Front-end Developer  
<br/>
  
## 🛠️ Server 기능

![image](https://github.com/sookmyung-graduation-project-2023/Server/assets/70003845/c3a57ba4-945a-4a76-99af-46aada547ce0)

LipRead는 기본적으로 REST API를 통해 클라이언트와 통신합니다. Python 또는 Node.js로 구현된 Lambda를 통해 전반적인 CRUD를 수행합니다.  
영상 생성 시 Lambda는 chat GPT를 통해 대화 텍스트를 생성하고 이를 EC2에 전송합니다. EC2는 OpenAI TTS를 통해 음성을 생성하고 DINet을 통해 대화 영상을 생성하며 이를 dynamoDB와 S3에 반영합니다.   
클라이언트는 CloudFront를 통해 S3에 저장된 영상을 스트리밍하며, Websocket API와 DynamoDB Stream을 통해 EC2의 영상 생성 진행 상황을 실시간으로 확인합니다.  
<br/>
Server 설명 (https://github.com/sookmyung-graduation-project-2023/Server/blob/main/README.md)  
<br/>  
## 🔎 상세 소개

- EC2
  - 인스턴스 유형: g4dn.xlarge
  - OS: ubuntu 20.04
  - Framework: FastAPI
- Model: DINet
  - Github: (https://github.com/MRzzm/DINet)
 
![image](https://github.com/sookmyung-graduation-project-2023/Server/assets/70003845/567ca23a-b176-45e8-a43e-9fc34c3ba638)

 Chat Roleplay- API를 통해 전송된 대화 텍스트와 Open AI의 TTS를 활용해 음성 파일을 생성합니다. 그 후 DINet을 통해 영상을 생성하고 생성된 영상을 S3에 저장합니다.   
 모든 대화 영상이 생성되면 클라이언트의 디바이스로 알림을 전송합니다.   
<br/>  
  
### 립싱크 영상 비교

![립싱크 영상 비교](https://github.com/sookmyung-graduation-project-2023/Server/assets/70003845/4ec1760a-e18d-484e-b61c-8a4aea3d7c05)
