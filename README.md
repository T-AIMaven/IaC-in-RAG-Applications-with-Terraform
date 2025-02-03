# Creating a RAG application with AWS CDK as IaC, Qdrant and LlamaIndex ☁️

<p align="center">
<img width="737" alt="cover_gke_medium" src="https://github.com/user-attachments/assets/66c13851-5894-4afe-8d2c-fcf488ce84ba">
</p>

This repository contains a full RAG application using AWS CDK as IaC, LlamaIndex framework, Qdrant as a vector database, and deployment on AWS using a FastAPI app and Dockerfile. 

For detailed project descriptions, refer to this [Medium article](https://medium.com/@benitomartin/creating-a-rag-application-with-aws-cdk-as-iac-qdrant-and-llamaindex-9138fd6999ef).

Main Steps

- **Data Ingestion**: Load data to an s3 bucket
- **Indexing**: Use SentenceSplitter for indexing in nodes
- **Embedding and Model**: OpenAI
- **Vector Store**: Use Qdrant for inserting metadata
- **FastAPI and AWS**: Handle requests via the FastAPI app deployed on AWS
- **IaC**: AWS CDK
  
Feel free to ⭐ and clone this repo 😉

## Tech Stack

![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![OpenAI](https://img.shields.io/badge/OpenAI-74aa9c?style=for-the-badge&logo=openai&logoColor=white)
![Anaconda](https://img.shields.io/badge/Anaconda-%2344A833.svg?style=for-the-badge&logo=anaconda&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=white)
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)


## Project Structure

The project has been structured with the following files:

- `app:` app logic with `Dockerfile`
- `tests`: unittest
- `app.py:` AWS CDK synthesizer
- `aws_cdk_rag_fargate:` script to create the constructs and stack
- `scripts:` scripts to puch the documents to s3 and create the Qdrant collection
- `.env:` environmental variables
- `requirements.txt:` project requirements


## Project Set Up

The Python version used for this project is Python 3.11. You can follow along the medium article.

1. Create an empty respository locally. This is necessary to initialize CDK. Afterwards you can copy the files from this repository.

2. Initialize AWS CDK to create the project structure:

   ```bash
   cdk init app --language python
   ```

3. Create the virtual environment named `main-env` using Conda with Python version 3.11:

   ```bash
   conda create -n main-env python=3.11
   conda activate main-env
   ```
   
4. Install the requirements.txt:

    ```bash
    pip install -r requirements.txt
    ```

5. Make sure the `.env` file is complete:

   ```bash
    QDRANT_URL=
    QDRANT_API_KEY=
    DOCUMENT_BUCKET=
    OPENAI_API_KEY=
   ```

6. Synthesize the app:

   ```bash
   cdk synth
   ```

7. Bootstrap the app to provision s3, ECR and IAM roles:
   
   ```bash
   cdk bootstrap aws://{Account ID:}/{region}
    ```

9. Create Qdrant Collection by running the script under `scripts`:
   
    ```bash
    python s3_uploader.py
    python qdrant_setup.py
    ```

10. Deploy the app on AWS CDK
 
    ```bash
    cdk deploy
    ```

11. Get the DNS Name

    ```bash
    aws cloudformation describe-stacks --stack-name AwsCdkRagFargateStack --query "Stacks[0].Outputs[?        OutputKey=='LoadBalancerDNS'].OutputValue" --output text

    # Output
    AwsCdk-RagFa-a1TpSwcX5iaS-653394042.eu-central-1.elb.amazonaws.com 
    ```
    
12. Send a POST request to test the app

    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"question":"What is a transformer?"}' http://AwsCdk-RagFa-a1TpSwcX5iaS-653394042.eu-central-1.elb.amazonaws.com/query
    ```

13. Clean up

    ```bash
    cdk destroy
    ```
