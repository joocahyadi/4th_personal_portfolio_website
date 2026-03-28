# Import Libraries
from firebase_functions import https_fn, options
from firebase_admin import initialize_app, firestore, _apps
from google.genai import Client
import json
import os

# 1. Initialize Services

# Firebase
if not _apps:
    initialize_app()

@https_fn.on_request(
        cors=options.CorsOptions(cors_origins="*", cors_methods=["POST", "OPTIONS"])
        , secrets=['GEMINI_API_KEY']
)
def ask_ai(req: https_fn.Request) -> https_fn.Response:

    db = firestore.client()

    # --- SECURITY ---
    if req.method == "OPTIONS":
        return https_fn.Response(status=204)
    
    try:

        # --- Step 1: Authentication to access Gemini ---
        api_key = os.environ.get('GEMINI_API_KEY')

        if not api_key:
            raise ValueError("Cloud secret 'GEMINI_API_KEY' not found.")
        
        client = Client(api_key=api_key)

        # --- Step 2: Parse user's questions ---
        request_json = req.get_json()
        user_query = request_json.get("data", {}).get("query", "Give me a brief introduction.")

        # --- Step 3: Data Retrieval --- 
        collections = ['educations', 'experiences','about']
        all_context = []

        for col in collections:
            # Stream each document in each collection
            docs = db.collection(col).stream()
            # for doc in docs:
                # data = doc.to_dict()  # This will result in a dictionary
                # # Transform the dictionary into a readable string
                # content = ', '.join([f'{k}: {v}' for k, v in data.items()])
                # # Tag
                # all_context.append(f'[{col.upper()}] {content}')
            data_list = [doc.to_dict() for doc in docs]

            all_context.append(f"### {col.upper()} DATA:\n{json.dumps(data_list, indent=2)}")

        
        # Merge all databases rows
        full_context = '\n\n'.join(all_context)

        # --- Step 4: AI Generation ---
        response = client.models.generate_content(
            model='gemini-2.5-flash'
            # model='gemini-2.5-pro'
            , config={
                'system_instruction': (
                    'You are the personal assistant for Joshia, a male person.'
                    'Use the provided database context to answer questions accurately.'
                    'If the answer is not in the data, then politely say you do not have that information yet, and ask the user to directly contact Joshia.'
                    'Do not be too stiff. You can have a more cheerful personality.'
                    'When answering questions, you MUST follow this 3 part structure separated by double line breaks:'
                    '1. Opening: A friendly, one-sentence acknowledgment of the user"s question. <double break>'
                    '2. Content: The detailed answer based on the provided database. Use multiple sentences and keep it engaging. <double break>'
                    '3. Closing: A call to action (can add one or two emojis) or a relevant link (if available).'
                    'CRITICAL: Do not use labels like "Opening:" or "Content:" in the actual response.'
                    'Always prioritize the provided CONTEXT. If the context conflicts with your prior knowledge, the context is the absolute truth.'
                )
            }
            , contents=f'Context from Database: \n {full_context} \n\n User Questions: {user_query}'
        )

        # --- Step 5: Return the response---
        return https_fn.Response(
            json.dumps({'data': {'text': response.text}})
            , mimetype='application/json'
        )


    except Exception as e:
        print(f'Deployment error: {str(e)}')
        return https_fn.Response(
            json.dumps({"data": {"text": "My brain is taking a quick break. Please try again in a moment!"}})
            , status=500
            , mimetype="application/json"
        )