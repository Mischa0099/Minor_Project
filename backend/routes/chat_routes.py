# backend/routes/chat_routes.py
from fastapi import FastAPI, HTTPException
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import warnings
warnings.filterwarnings("ignore")

import os
import re
import logging
import yaml
from datetime import datetime

# Try to import heavyweight ML packages lazily and fall back to simple functions if unavailable
# We'll set these at runtime inside ensure_models_loaded() to avoid blocking imports at app startup
HAS_TRANSFORMERS = False
HAS_GENAI = False
HAS_OPENAI = False
HAS_OLLAMA = False
pipeline = None
torch = None
genai = None

# We'll suppress model logs only if transformers gets imported during lazy load

# Initialize placeholders for lazy loading
sentiment_pipeline = None
chat_session = None  # Gemini session
openai_client = None  # OpenAI client
ollama_base_url = None  # Ollama base URL
text_generator = None  # Local transformers model
_models_loaded = False
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'response_templates.yaml')
response_templates = {}

USE_LOCAL_MODEL = os.getenv('USE_LOCAL_MODEL', 'false').lower() in ('1', 'true', 'yes')
# Default to False for development safety; enable by setting USE_GENAI=1 in your environment
USE_GENAI = os.getenv('USE_GENAI', 'false').lower() in ('1', 'true', 'yes')
# AI Provider Configuration
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')  # or 'gpt-4' for better quality
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')  # Default to mistral (smaller, uses less memory). Options: 'llama2', 'mistral', 'phi', 'tinyllama'
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')


def ensure_models_loaded():
    """Load models on first use. This keeps app startup quick and downloads happen only when needed.
    Priority order: OpenAI > Ollama > Gemini > Local transformers"""
    global sentiment_pipeline, chat_session, text_generator, _models_loaded
    global openai_client, ollama_base_url
    global HAS_OPENAI, HAS_OLLAMA, HAS_GENAI, HAS_TRANSFORMERS, pipeline, torch, genai
    
    # Always re-check, don't return early - this allows checking status
    # But only initialize once to avoid repeated API calls
    if _models_loaded and (HAS_OPENAI or HAS_OLLAMA or HAS_GENAI or text_generator):
        # Already loaded and has a provider, just return
        return
    
    if _models_loaded:
        # Models were loaded but no provider found, try again
        print("🔄 Re-checking AI providers...")
    
    _models_loaded = True

    # Lazy import transformers/torch if available
    try:
        from transformers import pipeline as _pipeline
        import torch as _torch
        pipeline = _pipeline
        torch = _torch
        HAS_TRANSFORMERS = True
        # suppress verbose transformers logs when loaded
        try:
            logging.getLogger("transformers").setLevel(logging.ERROR)
        except Exception:
            pass
    except Exception:
        HAS_TRANSFORMERS = False

    if HAS_TRANSFORMERS:
        try:
            print("(Lazy) Loading Sentiment Model... Please wait.\n")
            model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
            device = 0 if (torch and getattr(torch, 'cuda', None) and torch.cuda.is_available()) else -1
            sentiment_pipeline = pipeline("sentiment-analysis", model=model_name, device=device)
            print("✅ Sentiment Model loaded successfully!\n")
        except Exception as e:
            print("Could not load transformers sentiment model:", e)
            sentiment_pipeline = None

        if USE_LOCAL_MODEL:
            try:
                print("(Lazy) Loading local text-generation model (distilgpt2)...")
                gen_model = 'distilgpt2'
                gen_device = 0 if (torch and getattr(torch, 'cuda', None) and torch.cuda.is_available()) else -1
                text_generator = pipeline('text-generation', model=gen_model, device=gen_device)
                print("✅ Local text-generation model loaded.")
            except Exception as e:
                print('Failed to load local text-generation model:', e)
                text_generator = None

    # PRIORITY 1: Lazy import OpenAI (most stable, recommended)
    try:
        from openai import OpenAI
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and api_key.strip():
            try:
                openai_client = OpenAI(api_key=api_key)
                # Test the client by checking if it's properly initialized
                HAS_OPENAI = True
                print(f'✅ OpenAI configured (lazy) - Model: {OPENAI_MODEL}')
            except Exception as init_error:
                HAS_OPENAI = False
                openai_client = None
                print(f'❌ OpenAI initialization failed: {init_error}')
        else:
            print('ℹ️ OPENAI_API_KEY not set or empty. OpenAI will be skipped.')
            HAS_OPENAI = False
            openai_client = None
    except ImportError:
        HAS_OPENAI = False
        openai_client = None
        print('ℹ️ OpenAI package not installed. Install with: pip install openai')
    except Exception as e:
        HAS_OPENAI = False
        openai_client = None
        print(f"❌ Could not initialize OpenAI: {e}")
        import traceback
        traceback.print_exc()

    # PRIORITY 2: Ollama (local, free, no API key needed)
    # Always check Ollama as it can be a fallback even if OpenAI is available
    try:
        import requests
        # Test if Ollama is available
        test_url = f"{OLLAMA_BASE_URL}/api/tags"
        response = requests.get(test_url, timeout=2)
        if response.status_code == 200:
            ollama_base_url = OLLAMA_BASE_URL
            HAS_OLLAMA = True
            print(f'✅ Ollama configured (lazy) - Base URL: {OLLAMA_BASE_URL}, Model: {OLLAMA_MODEL}')
        else:
            HAS_OLLAMA = False
            ollama_base_url = None
            print(f'ℹ️ Ollama not available at {OLLAMA_BASE_URL} (status: {response.status_code}). Install from https://ollama.ai')
    except requests.exceptions.ConnectionError:
        HAS_OLLAMA = False
        ollama_base_url = None
        print(f'ℹ️ Ollama not running at {OLLAMA_BASE_URL}. Start Ollama or install from https://ollama.ai')
    except Exception as e:
        HAS_OLLAMA = False
        ollama_base_url = None
        print(f'ℹ️ Ollama check failed: {type(e).__name__}: {e}. Install from https://ollama.ai')

    # PRIORITY 3: Lazy import Google Generative AI if available
    try:
        import google.generativeai as _genai
        genai = _genai
        HAS_GENAI = True
    except Exception:
        HAS_GENAI = False

    if HAS_GENAI and USE_GENAI and genai is not None:
        try:
            # Check for API key before configuring
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                print('ℹ️ GOOGLE_API_KEY not set. Gemini generation will be skipped.')
                chat_session = None
            else:
                genai.configure(api_key=api_key)
                gemini_model = genai.GenerativeModel("gemini-pro")
                # Start chat session without history here; we pass history in the prompt for better control
                chat_session = gemini_model.start_chat(history=[])
                print('✅ Google Generative AI (Gemini) configured (lazy)')
        except Exception as e:
            print("Could not initialize Google Generative AI:", e)
            chat_session = None
    
    # Load response templates if available (separate try/except)
    global response_templates
    try:
        with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            response_templates = yaml.safe_load(f) or {}
            print('✅ Loaded response templates')
    except Exception:
        response_templates = {}


def analyze_sentiment(text):
    """Analyzes sentiment using transformers if available, otherwise a naive heuristic."""
    ensure_models_loaded()
    # Symptom keywords that should lean negative even if a generic model is uncertain
    symptom_negative_terms = [
        'nausea','nauseous','vomit','vomiting','sick to my stomach','fever','high fever','temperature','chills',
        'headache','migraine','dizzy','dizziness','pain','sore throat','cough','flu','ill','sick'
    ]
    if sentiment_pipeline:
        try:
            result = sentiment_pipeline(text)[0]
            label = result.get('label', 'NEUTRAL').upper()
            # Some transformers return labels like 'LABEL_0' or 'NEGATIVE' - normalize
            if label.startswith('LABEL_'):
                # heuristic mapping: assume LABEL_0 negative, LABEL_1 neutral, LABEL_2 positive
                try:
                    idx = int(label.split('_', 1)[1])
                    label = {0: 'NEGATIVE', 1: 'NEUTRAL', 2: 'POSITIVE'}.get(idx, 'NEUTRAL')
                except Exception:
                    label = 'NEUTRAL'
            # clamp score to 0-100 and format as float
            raw = float(result.get('score', 0.0)) * 100.0
            # Clamp score to 1-100 inclusive and ensure float
            score = float(max(1.0, min(100.0, raw)))

            # Post-adjust for clear symptom terms: force NEGATIVE with a stronger score
            try:
                t_low = (text or '').lower()
                if any(term in t_low for term in symptom_negative_terms):
                    if label != 'NEGATIVE' or score < 75.0:
                        label = 'NEGATIVE'
                        score = max(80.0, score)
            except Exception:
                pass
            return label, round(score, 2)
        except Exception:
            pass

    # Fallback: very simple keyword-based sentiment
    text_low = (text or "").lower()
    # Health symptom indicators should be negative
    if any(w in text_low for w in symptom_negative_terms):
        return 'NEGATIVE', 85.0
    if any(w in text_low for w in ['good', 'great', 'happy', 'love', 'excellent']):
        return 'POSITIVE', 90.0
    if any(w in text_low for w in ['bad', 'sad', 'terrible', 'hate', 'awful']):
        return 'NEGATIVE', 90.0
    return 'NEUTRAL', 50.0

def get_user_profile_context(user_id):
    """Fetches user profile and formats it as a comprehensive personalized context for the AI."""
    context = ""
    try:
        from models import Profile
        profile = Profile.query.filter_by(user_id=user_id).first()
        if profile:
            # Build a detailed, structured profile context for personalization
            profile_sections = []
            
            # Basic demographics
            if profile.name:
                profile_sections.append(f"Patient Name: {profile.name}")
            if profile.age:
                profile_sections.append(f"Age: {profile.age} years")
            if profile.gender:
                profile_sections.append(f"Gender: {profile.gender}")
            if profile.weight:
                profile_sections.append(f"Weight: {profile.weight} kg")
            
            # Health conditions - critical for personalization
            if profile.health_conditions and str(profile.health_conditions).strip().lower() not in ('none', 'n/a', ''):
                profile_sections.append(f"\nCurrent Health Conditions:\n{profile.health_conditions}")
            
            # Medication history - very important for personalized advice
            if profile.previous_medication_history and str(profile.previous_medication_history).strip().lower() not in ('none', 'n/a', ''):
                profile_sections.append(f"\nPatient's Previous Medication History:\n{profile.previous_medication_history}")
            
            # Family history - important for risk assessment
            if profile.family_medication_history and str(profile.family_medication_history).strip().lower() not in ('none', 'n/a', ''):
                profile_sections.append(f"\nFamily Medication/Medical History:\n{profile.family_medication_history}")
            
            # Response style preference
            response_style = getattr(profile, 'response_style', 'concise') or 'concise'
            
            context = "\n".join(profile_sections)
            
            # Add a note about response style at the end
            if context:
                context += f"\n\nResponse Style Preference: {response_style}"
                
    except Exception as e:
        print(f"Error fetching profile context for user {user_id}: {e}")
    return context

def generate_rule_based_response(message, sentiment_label, sentiment_score=None, history_text='', profile_context=''):
    """Generate a personalized response tailored to the sentiment and user profile, as a fallback when AI is unavailable."""
    ensure_models_loaded()

    # Build a practical, health-focused response depending on sentiment
    sentiment_label_up = (sentiment_label or 'NEUTRAL').upper()

    # Extract profile information for personalization
    user_name = None
    user_age = None
    user_weight = None
    health_conditions = None
    medication_history = None
    family_history = None
    
    try:
        if profile_context:
            # Extract name
            if 'Patient Name:' in profile_context:
                try:
                    user_name = profile_context.split('Patient Name:')[1].split('\n')[0].strip()
                except:
                    pass
            
            # Extract age
            if 'Age:' in profile_context:
                try:
                    age_str = profile_context.split('Age:')[1].split('years')[0].strip()
                    user_age = int(age_str) if age_str.isdigit() else None
                except:
                    pass
            
            # Extract weight
            if 'Weight:' in profile_context:
                try:
                    weight_str = profile_context.split('Weight:')[1].split('kg')[0].strip()
                    user_weight = float(weight_str) if weight_str.replace('.', '').isdigit() else None
                except:
                    pass
            
            # Extract health conditions
            if 'Current Health Conditions:' in profile_context:
                try:
                    conditions_section = profile_context.split('Current Health Conditions:')[1]
                    if '\nPatient' in conditions_section:
                        health_conditions = conditions_section.split('\nPatient')[0].strip()
                    elif '\nFamily' in conditions_section:
                        health_conditions = conditions_section.split('\nFamily')[0].strip()
                    else:
                        health_conditions = conditions_section.split('\n\n')[0].strip()
                except:
                    pass
            
            # Extract medication history
            if "Patient's Previous Medication History:" in profile_context:
                try:
                    med_section = profile_context.split("Patient's Previous Medication History:")[1]
                    if '\nFamily' in med_section:
                        medication_history = med_section.split('\nFamily')[0].strip()
                    else:
                        medication_history = med_section.split('\n\n')[0].strip()
                except:
                    pass
            
            # Extract family history
            if 'Family Medication/Medical History:' in profile_context:
                try:
                    family_section = profile_context.split('Family Medication/Medical History:')[1]
                    family_history = family_section.split('\n\n')[0].strip()
                except:
                    pass
    except Exception as e:
        print(f"Error parsing profile context: {e}")
        pass

    # Derive response style from profile_context if provided
    response_style = 'concise'
    try:
        if 'Response Style Preference: detailed' in profile_context:
            response_style = 'detailed'
    except Exception:
        response_style = 'concise'

    # Helper: format percentage safely
    try:
        pct = float(sentiment_score or 0.0)
        pct = max(0.0, min(100.0, pct))
    except Exception:
        pct = 0.0

    # Derive coarse topic from history + current message to keep continuity without heavy NLP
    try:
        def extract_topic(text):
            stop = set(['the','is','are','a','an','and','or','to','of','in','on','for','with','it','this','that','you','i','me','my','your','we','our'])
            words = re.findall(r"[a-zA-Z][a-zA-Z\-']+", (text or '').lower())
            counts = {}
            for w in words:
                if w in stop or len(w) < 3:
                    continue
                counts[w] = counts.get(w, 0) + 1
            if not counts:
                return None
            # prefer words that occur >1 across history+message if available
            sorted_items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
            top_word, top_count = sorted_items[0]
            return top_word if top_count >= 2 else top_word

        topic = extract_topic((history_text or '') + ' ' + (message or ''))
    except Exception:
        topic = None
        
    # Symptom-specific guidance: detect common symptoms and provide reasons + steps
    msg = (message or '').lower()
    symptoms = []
    if any(w in msg for w in ['nausea', 'nauseous', 'vomit', 'sick to my stomach']):
        symptoms.append('nausea')
    if any(w in msg for w in ['headache', 'migraine', 'pain in head']):
        symptoms.append('headache')
    if any(w in msg for w in ['dizzy', 'dizziness', 'see clearly', 'vision']):
        symptoms.append('dizziness')

    # Build reasons and suggestions for common symptoms
    reason_lines = []
    suggestions = []
    red_flags = []
    if 'nausea' in symptoms:
        reason_lines.append("Common causes of nausea include viral gastroenteritis (stomach flu), food poisoning, medication side effects, migraines, motion sickness, pregnancy, or acid reflux.")
        suggestions.extend([
            "Try to rest and avoid strong smells.",
            "Sip small amounts of clear fluids (water, oral rehydration) to avoid dehydration.",
            "Eat bland foods (toast, crackers, bananas) if you can tolerate them.",
            "Avoid alcohol and heavy fatty meals until symptoms improve."
        ])
        red_flags.extend([
            "High fever with severe abdominal pain",
            "Repeated vomiting and inability to keep fluids down",
            "Signs of dehydration (very little urine, dizziness when standing)",
            "Blood in vomit or black stools"
        ])
    if 'dizziness' in symptoms:
        reason_lines.append("Dizziness can be caused by low blood pressure, dehydration, inner ear issues, low blood sugar, or medication effects.")
        suggestions.extend([
            "Sit or lie down until the feeling passes and get up slowly.",
            "Ensure you are hydrated and have eaten something light if you haven't in a while."
        ])
        red_flags.append("Sudden severe dizziness with difficulty speaking or weakness — seek emergency care.")

    # Personalized tone and greeting
    greeting = ""
    if user_name:
        greeting = f"Hello {user_name}, "
    
    if sentiment_label_up.startswith('NEG'):
        empathic = f"{greeting}I'm sorry you're experiencing this — I hear you."
    elif sentiment_label_up.startswith('POS'):
        empathic = f"{greeting}I'm glad to hear some positive signs — let's build on that."
    else:
        empathic = f"{greeting}Thanks for sharing — I want to help." 

    # If message appears to be non-health/relationship/social request and no symptoms detected,
    # provide a generic helpful reply rather than keep asking for symptoms.
    non_health_triggers = ['friend', 'friends', 'relationship', 'advice', 'suggest', 'suggestion', 'how to', 'how do', 'relationship']
    is_non_health = any(t in msg for t in non_health_triggers) and not symptoms

    # Compose response depending on response_style
    if response_style == 'detailed':
        parts = [empathic]
        if topic:
            parts.append(f"\nTopic: {topic}")
        if reason_lines:
            parts.append('\nReasons: ' + ' '.join(reason_lines))
        if suggestions:
            parts.append('\nWhat you can try now:')
            for s in suggestions:
                parts.append(f"- {s}")
        if red_flags:
            parts.append('\nWhen to seek urgent care:')
            for r in red_flags:
                parts.append(f"- {r}")
        parts.append(f"\nSentiment: {sentiment_label_up} ({pct}%)")
        parts.append('\nIf you want, I can suggest a short breathing or grounding exercise, or help you decide whether to contact a provider.')
        return '\n'.join(parts)
    else:
        # concise
        prefix = f"[{topic}] " if topic else ""
        if reason_lines:
            main = f"{empathic} Possible causes include: {reason_lines[0]} Try sipping small amounts of fluid, resting, and eating bland foods if tolerated."
        elif is_non_health:
            # short, actionable non-health advice
            main = f"{empathic} {prefix}For questions about friends or relationships, try to be specific about the situation — e.g., what happened, how it made you feel, and what outcome you want. If you'd like, tell me one detail and I can suggest a next step."
        else:
            # Personalized generic fallback using profile data
            personalization = ""
            
            # Add personalized context based on profile
            if user_age:
                if user_age < 18:
                    personalization += "As someone under 18, "
                elif user_age > 65:
                    personalization += "Given your age, "
            
            if health_conditions:
                # Extract first condition for personalization
                first_condition = health_conditions.split(',')[0].split('.')[0].strip()
                if first_condition:
                    personalization += f"and considering you have {first_condition}, "
            
            if medication_history:
                personalization += "I'll keep your medication history in mind. "
            
            if not personalization:
                personalization = "Based on your profile, "
            
            main = f"{empathic} {personalization}{prefix}Could you tell me when this started or how severe it is? A quick detail helps me give a more useful suggestion tailored to your situation."

        # append red flag hint concisely
        if red_flags:
            main += f" If you have severe pain, repeated vomiting, or dehydration signs, please seek urgent care."
        main += f" Sentiment: {sentiment_label_up} ({pct}%)"
        return main


def generate_ai_response(message, history_text='', profile_context='', sentiment_label='NEUTRAL', sentiment_score=50.0):
    """Generates a personalized AI response based on user profile, medical history, and context.
    Priority: OpenAI > Ollama > Gemini > Local transformers. Returns None on failure/disabled."""
    ensure_models_loaded()
    
    # Determine response style from profile context
    response_style = 'concise'
    if 'Response Style Preference: detailed' in profile_context:
        response_style = 'detailed'
    
    # Build comprehensive personalized prompt
    system_instructions = """You are a personalized healthcare AI assistant. Your responses MUST be:
1. PERSONALIZED - Tailored specifically to the patient's profile (age, weight, gender, health conditions, medication history, family history)
2. CONTEXT-AWARE - Consider all medical history when giving advice
3. SAFE - Never prescribe medications, always recommend consulting healthcare providers for serious concerns
4. EMPATHETIC - Match the patient's emotional state based on sentiment analysis
5. RELEVANT - Stay focused on the patient's specific health context"""
    
    # Build the personalized context section
    personalized_section = ""
    if profile_context and profile_context.strip():
        personalized_section = f"""PATIENT PROFILE FOR PERSONALIZATION:
{profile_context}

IMPORTANT: Use this profile to personalize ALL responses:
- Consider the patient's age when suggesting remedies (e.g., children vs elderly need different approaches)
- Consider weight when discussing medication interactions or dosage-related concerns
- Factor in existing health conditions when giving any advice
- Consider medication history to avoid suggesting things that might interact with their medications
- Factor in family medical history for risk assessment
- Personalize the conversation naturally based on these factors, don't just list generic advice"""
    else:
        personalized_section = "Note: Limited patient profile available. Provide general health advice but encourage patient to complete their profile for better personalization."
    
    # Build conversation history context
    history_section = ""
    if history_text and history_text.strip():
        history_section = f"""RECENT CONVERSATION HISTORY:
{history_text}

Use this history to maintain conversation continuity and context."""
    
    # Build sentiment-aware guidance
    sentiment_guidance = ""
    if sentiment_label:
        sentiment_upper = sentiment_label.upper()
        if sentiment_upper == 'NEGATIVE':
            sentiment_guidance = f"The patient is expressing negative emotions (sentiment score: {sentiment_score}%). Be extra empathetic, supportive, and reassuring. Focus on understanding and providing comfort while addressing their concerns."
        elif sentiment_upper == 'POSITIVE':
            sentiment_guidance = f"The patient seems positive (sentiment score: {sentiment_score}%). Maintain an encouraging, friendly tone and build on their positive state."
        else:
            sentiment_guidance = f"The patient's sentiment is neutral. Provide clear, balanced information and support."
    
    # Build user message with instructions
    user_message_content = f"""{personalized_section}

{history_section}

{sentiment_guidance}

CURRENT PATIENT MESSAGE: {message}

INSTRUCTIONS:
- Provide a personalized response that directly references the patient's specific profile factors (age, weight, health conditions, medication history) when relevant
- If remedies or suggestions are requested, personalize them based on the patient's age, weight, existing conditions, and medication history
- Do NOT use generic "if you have X, do Y" statements - instead, speak directly to the patient using their name and specific context
- For medication or treatment suggestions, always consider potential interactions with their existing medications and conditions
- Keep responses {response_style} per patient preference, but ensure personalization is never sacrificed
- Respond naturally as if you know this patient personally, referencing their specific health context when giving advice"""

    # PRIORITY 1: Try OpenAI (most stable, recommended)
    if HAS_OPENAI and openai_client:
        try:
            response = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_instructions},
                    {"role": "user", "content": user_message_content}
                ],
                temperature=0.7,
                max_tokens=500
            )
            response_text = response.choices[0].message.content.strip()
            if response_text:
                return response_text
        except Exception as e:
            print(f'OpenAI generation failed: {e}')
    
    # PRIORITY 2: Try Ollama (local, free, no API key)
    if HAS_OLLAMA and ollama_base_url:
        try:
            import requests
            ollama_prompt = f"""{system_instructions}

{user_message_content}

Generate your personalized response now:"""
            
            response = requests.post(
                f"{ollama_base_url}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": ollama_prompt,
                    "stream": False
                },
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '').strip()
                if response_text:
                    return response_text
        except Exception as e:
            print(f'Ollama generation failed: {e}')
    
    # PRIORITY 3: Try Gemini if available
    if chat_session:
        try:
            final_prompt = f"""{system_instructions}

{user_message_content}

Generate your personalized response now:"""
            
            response = chat_session.send_message(final_prompt)
            response_text = getattr(response, 'text', str(response)).strip()
            
            if response_text and len(response_text) > 20:
                return response_text
        except Exception as e:
            print(f'Gemini generation failed: {e}')

    # PRIORITY 4: Try local generator if configured (fallback, less ideal for personalization)
    if text_generator:
        try:
            final_prompt = f"""{system_instructions}

{user_message_content}

Generate your personalized response now:"""
            
            outputs = text_generator(
                final_prompt,
                max_length=200,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                repetition_penalty=1.2,
                no_repeat_ngram_size=3,
                num_return_sequences=1,
                temperature=0.7,
            )
            if outputs and isinstance(outputs, list):
                text = outputs[0].get('generated_text') or outputs[0].get('text') or str(outputs[0])
                # Remove the original prompt which the model might echo
                text = text.replace(final_prompt, '').strip()
                # Clean up and keep first few sentences
                sentences = re.split(r'(?<=[.!?])\s+', text)
                return ' '.join(sentences[:4]).strip()
        except Exception as e:
            print(f'Local generation failed: {e}')

    # Returns None if all providers failed
    return None


from db import db
from models import ChatHistory, User, Profile, Alert, Conversation

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/', methods=['POST'])
@jwt_required()
def chat():
    data = request.get_json() or {}
    message = data.get('message')
    conversation_id = data.get('conversation_id')

    if not message:
        return jsonify({'message': 'Message required'}), 400

    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except Exception:
        # If identity wasn't stored as int, leave as-is
        pass

    # 1. Handle Quick Greeting (priority 1) - personalized greeting using AI if available
    try:
        # Quick greeting detection: if user says 'hi' / 'hello' / 'hey' variants
        msg_low = (message or '').strip().lower()
        if msg_low and re.match(r"^\s*(hi+|hello|hey|hiya|hii)\b", message, re.IGNORECASE):
            # Get profile context for personalized greeting
            profile_context = get_user_profile_context(user_id)
            ensure_models_loaded()
            
            # Try AI-powered personalized greeting using priority system
            ai_response = None
            greeting_prompt = f"""Generate a warm, personalized greeting for this healthcare conversation.

PATIENT PROFILE:
{profile_context if profile_context else 'New patient'}

The patient just said: "{message}"

Create a friendly, personalized greeting that:
1. Uses their name if available
2. Acknowledges their profile context naturally (e.g., if they have health conditions, acknowledge readiness to help with their specific needs)
3. Is warm, professional, and inviting
4. Keeps it to 1-2 sentences
5. Sets a supportive tone for a healthcare conversation

Generate the personalized greeting:"""
            
            greeting_system = "You are a friendly healthcare AI assistant. Create warm, personalized greetings."
            
            try:
                # Try OpenAI first
                if HAS_OPENAI and openai_client:
                    try:
                        response = openai_client.chat.completions.create(
                            model=OPENAI_MODEL,
                            messages=[
                                {"role": "system", "content": greeting_system},
                                {"role": "user", "content": greeting_prompt}
                            ],
                            temperature=0.8,
                            max_tokens=150
                        )
                        ai_response = response.choices[0].message.content.strip()
                    except Exception:
                        pass
                
                # Try Ollama if OpenAI failed
                if not ai_response and HAS_OLLAMA and ollama_base_url:
                    try:
                        import requests
                        response = requests.post(
                            f"{ollama_base_url}/api/generate",
                            json={
                                "model": OLLAMA_MODEL,
                                "prompt": f"{greeting_system}\n\n{greeting_prompt}",
                                "stream": False
                            },
                            timeout=10
                        )
                        if response.status_code == 200:
                            result = response.json()
                            ai_response = result.get('response', '').strip()
                    except Exception:
                        pass
                
                # Try Gemini if others failed
                if not ai_response and chat_session:
                    try:
                        response = chat_session.send_message(greeting_prompt)
                        ai_response = getattr(response, 'text', str(response)).strip()
                    except Exception:
                        pass
            except Exception:
                pass
            
            # Fallback to personalized greeting using profile context
            if not ai_response:
                # Extract name from profile context
                name = None
                if profile_context and 'Patient Name:' in profile_context:
                    try:
                        name = profile_context.split('Patient Name:')[1].split('\n')[0].strip()
                    except:
                        pass
                
                # Try database if not in context
                if not name:
                    try:
                        profile = Profile.query.filter_by(user_id=user_id).first()
                        if profile and getattr(profile, 'name', None):
                            name = profile.name
                    except Exception:
                        pass

                # Build personalized greeting
                if name:
                    # Check for health conditions to make greeting more relevant
                    has_conditions = profile_context and 'Current Health Conditions:' in profile_context
                    if has_conditions:
                        ai_response = f"Hello {name}! I'm here to help you with your health questions. I see you have some health conditions in your profile - I'll keep those in mind when assisting you. How can I help you today?"
                    else:
                        ai_response = f"Hello {name}! I'm here to help you with your health questions. How can I assist you today?"
                else:
                    ai_response = "Hello! I'm here to help you with your health questions. How can I assist you today?"

            sentiment_label, sentiment_score = 'NEUTRAL', 50.0

            # save chat entry (best-effort)
            try:
                chat_entry = ChatHistory(
                    user_id=user_id,
                    user_message=message,
                    ai_response=ai_response,
                    sentiment_label=sentiment_label,
                    sentiment_score=sentiment_score
                )
                db.session.add(chat_entry)
                db.session.commit()
            except Exception as e:
                try:
                    db.session.rollback()
                except Exception:
                    pass
                print('Failed to save greeting chat entry:', e)

            return jsonify({'user_message': message, 'ai_response': ai_response, 'sentiment': {'label': sentiment_label, 'score': round(float(sentiment_score),2)}, 'alert': None}), 200
    except Exception:
        # if greeting logic fails for any reason, continue to normal flow
        pass
    
    # 2. Analyze sentiment (priority 2)
    sentiment_label, sentiment_score = analyze_sentiment(message)

    # 3. Handle Urgent Help Detection (priority 3)
    try:
        msg_low = (message or '').strip().lower()
        urgent_triggers = [
            'urgent', 'help needed', 'need help', 'i need help', 'emergency', 'call an ambulance',
            'suicid', 'i want to die', 'kill myself', 'hurt myself', 'immediately', 'in danger', 'help me now'
        ]
        is_urgent = any(t in msg_low for t in urgent_triggers)
    except Exception:
        is_urgent = False

    if is_urgent:
        # escalate immediately - but still try to personalize the response
        try:
            # treat as severe negative
            sentiment_label = 'NEGATIVE'
            sentiment_score = 95.0
            
            # Try to get personalized urgent response using AI (priority: OpenAI > Ollama > Gemini > Local)
            profile_context = get_user_profile_context(user_id)
            ensure_models_loaded()
            
            urgent_prompt = f"""URGENT SITUATION - IMMEDIATE RESPONSE NEEDED

PATIENT PROFILE:
{profile_context if profile_context else 'Limited profile available'}

PATIENT URGENT MESSAGE: {message}

The patient is expressing an urgent need for help. Provide an empathetic, personalized, and immediate response that:
1. Acknowledges their distress personally (use their name if available)
2. Provides immediate crisis support information
3. Takes into account their age, health conditions, and medical history when giving safety advice
4. Is warm, supportive, and action-oriented
5. Directs them to immediate help (emergency services, crisis lines)
6. Keeps it concise but personalized - this is an emergency

Generate an immediate, personalized urgent response:"""
            
            # Use the AI response generator with urgent prompt
            ai_response = None
            try:
                # Build system instructions for urgent situation
                urgent_system = "You are a healthcare AI assistant responding to an urgent crisis situation. Be immediate, empathetic, and action-oriented."
                
                # Try OpenAI first (most reliable)
                if HAS_OPENAI and openai_client:
                    try:
                        response = openai_client.chat.completions.create(
                            model=OPENAI_MODEL,
                            messages=[
                                {"role": "system", "content": urgent_system},
                                {"role": "user", "content": urgent_prompt}
                            ],
                            temperature=0.8,
                            max_tokens=300
                        )
                        ai_response = response.choices[0].message.content.strip()
                    except Exception:
                        pass
                
                # Try Ollama if OpenAI failed
                if not ai_response and HAS_OLLAMA and ollama_base_url:
                    try:
                        import requests
                        response = requests.post(
                            f"{ollama_base_url}/api/generate",
                            json={
                                "model": OLLAMA_MODEL,
                                "prompt": f"{urgent_system}\n\n{urgent_prompt}",
                                "stream": False
                            },
                            timeout=15
                        )
                        if response.status_code == 200:
                            result = response.json()
                            ai_response = result.get('response', '').strip()
                    except Exception:
                        pass
                
                # Try Gemini if others failed
                if not ai_response and chat_session:
                    try:
                        response = chat_session.send_message(urgent_prompt)
                        ai_response = getattr(response, 'text', str(response)).strip()
                    except Exception:
                        pass
            except Exception:
                pass
            
            # Fallback to generic urgent response if AI unavailable
            if not ai_response:
                user_name = ""
                if profile_context and "Patient Name:" in profile_context:
                    try:
                        user_name = profile_context.split("Patient Name:")[1].split("\n")[0].strip()
                    except:
                        pass
                
                if user_name:
                    ai_response = f"I hear you, {user_name} — it sounds like you're in urgent distress. If you are in immediate danger, please call your local emergency number now (for example, 911 in the US). If you are able, consider contacting a crisis line or a trusted person nearby. I'm here to help you stay safe right now."
                else:
                    ai_response = "I hear you — it sounds like you're in urgent distress. If you are in immediate danger, please call your local emergency number now (for example, 911 in the US). If you are able, consider contacting a crisis line or a trusted person nearby. I'm here to help you stay safe right now."
            
            # Save chat history
            chat_entry = ChatHistory(
                user_id=user_id,
                user_message=message,
                ai_response=ai_response,
                sentiment_label=sentiment_label,
                sentiment_score=sentiment_score
            )
            db.session.add(chat_entry)
            db.session.commit()

            # create alert record
            try:
                msg = 'Immediate urgent help trigger from user message.'
                alert = Alert(user_id=user_id, alert_type='urgent', message=msg)
                db.session.add(alert)
                db.session.commit()
                alert_info = {'alert_id': alert.id, 'message': msg}
            except Exception:
                alert_info = {'message': 'Alert creation failed'}

            return jsonify({'user_message': message, 'ai_response': ai_response, 'sentiment': {'label': sentiment_label, 'score': round(float(sentiment_score),2)}, 'alert': alert_info}), 200
        except Exception:
            # Fall back to normal flow if saving/alerting fails
            try:
                db.session.rollback()
            except Exception:
                pass

    # 4. Prepare Context for AI/Rule-based System
    profile_context = get_user_profile_context(user_id)

    # Compose a short history string from recent chat entries for this user (last 6)
    history_text = ''
    try:
        q = ChatHistory.query.filter_by(user_id=user_id)
        if conversation_id:
            try:
                conversation_id = int(conversation_id)
                q = q.filter_by(conversation_id=conversation_id)
            except Exception:
                pass
        recent = q.order_by(ChatHistory.created_at.desc()).limit(6).all()
        if recent:
            recent = list(reversed(recent))
            pairs = []
            for entry in recent:
                pairs.append(f"User: {entry.user_message} | AI: {entry.ai_response}")
            history_text = '\n'.join(pairs) + '\n'
    except Exception:
        history_text = ''


    # 5. Generate Response - PRIORITIZE AI (Gemini/Local) for personalized responses
    ai_response = None
    
    # Always try AI first if available - it provides personalized responses
    # Ensure models are loaded and get current status
    ensure_models_loaded()
    
    # Debug: Print AI provider status
    print(f"\n🔍 AI Provider Status Check for user {user_id}:")
    print(f"   HAS_OPENAI: {HAS_OPENAI}, openai_client: {openai_client is not None}")
    print(f"   HAS_OLLAMA: {HAS_OLLAMA}, ollama_base_url: {ollama_base_url}")
    print(f"   HAS_GENAI: {HAS_GENAI}, chat_session: {chat_session is not None}")
    print(f"   USE_GENAI: {USE_GENAI}")
    print(f"   text_generator: {text_generator is not None}")
    
    # Check if any AI provider is available (OpenAI, Ollama, Gemini, or Local)
    has_ai_provider = (HAS_OPENAI and openai_client) or (HAS_OLLAMA and ollama_base_url) or (chat_session is not None) or (text_generator is not None)
    
    if has_ai_provider:
        print(f"✅ AI provider detected! Attempting to generate personalized response...")
        try:
            # Call the LLM with full context including sentiment for personalized response
            ai_response = generate_ai_response(
                message, 
                history_text=history_text, 
                profile_context=profile_context,
                sentiment_label=sentiment_label,
                sentiment_score=sentiment_score
            )
            if ai_response:
                print(f"✅ Generated personalized AI response for user {user_id}")
            else:
                print(f"⚠️ AI provider available but returned None - falling back to rule-based")
        except Exception as e:
            print(f"❌ Error during AI model call: {e}")
            import traceback
            traceback.print_exc()
            ai_response = None 
    else:
        print("⚠️ WARNING: No AI model available. Current status:")
        print(f"   OpenAI: HAS_OPENAI={HAS_OPENAI}, client={openai_client is not None}")
        print(f"   Ollama: HAS_OLLAMA={HAS_OLLAMA}, url={ollama_base_url}")
        print(f"   Gemini: HAS_GENAI={HAS_GENAI}, USE_GENAI={USE_GENAI}, session={chat_session is not None}")
        print(f"   Local: text_generator={text_generator is not None}")
        print("\n💡 To enable AI responses:")
        print("   - Set OPENAI_API_KEY for OpenAI (recommended, most stable)")
        print("   - Install Ollama (free, local): https://ollama.ai")
        print("   - Set GOOGLE_API_KEY and USE_GENAI=1 for Gemini")
        print("   - Set USE_LOCAL_MODEL=1 for local transformers")

    # CHECK 2: Only use rule-based fallback if AI completely unavailable or failed
    if ai_response is None or not ai_response.strip():
        print(f"⚠️ Falling back to rule-based response (less personalized) for user {user_id}")
        # Use rule-based response as the final guaranteed fallback
        # This is minimal - only used when AI completely unavailable
        ai_response = generate_rule_based_response(
            message, 
            sentiment_label, 
            sentiment_score, 
            history_text, 
            profile_context
        )
        if ai_response:
            print(f"⚠️ Used generic rule-based response. Recommend enabling AI (Gemini) for personalized responses.")
    
    # 6. Save to Database
    try:
        chat_entry = ChatHistory(
            user_id=user_id,
            conversation_id=conversation_id if isinstance(conversation_id, int) else None,
            user_message=message,
            ai_response=ai_response,
            sentiment_label=sentiment_label,
            sentiment_score=sentiment_score
        )
        db.session.add(chat_entry)
        db.session.commit()
    except Exception as e:
        print('DB save failed:', e)

    # 7. Check for Alerts (post-response)
    alert_info = None
    try:
        recent = ChatHistory.query.filter_by(user_id=user_id).order_by(ChatHistory.created_at.desc()).limit(2).all()
        if len(recent) == 2:
            first, second = recent[0], recent[1]
            if first.sentiment_label == 'NEGATIVE' and second.sentiment_label == 'NEGATIVE' and first.sentiment_score >= 85.0 and second.sentiment_score >= 85.0:
                msg = 'Consecutive high-severity negative sentiments detected. Please check in with the user.'
                alert = Alert(user_id=user_id, alert_type='mental_health_risk', message=msg)
                db.session.add(alert)
                db.session.commit()
                alert_info = {'alert_id': alert.id, 'message': msg}
    except Exception:
        alert_info = None

    return jsonify({
        'user_message': message,
        'ai_response': ai_response,
        'sentiment': {
            'label': sentiment_label,
            'score': sentiment_score
        },
        'alert': alert_info
    }), 200

# Other routes (history, conversations, conversation_detail) remain the same
@chat_bp.route('/history', methods=['GET'])
@jwt_required()
def history():
    """Return recent chat history for the authenticated user (default last 50)."""
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except Exception:
        pass

    try:
        limit_param = request.args.get('limit', '50')
        limit = int(limit_param)
        limit = max(1, min(200, limit))
    except Exception:
        limit = 50

    try:
        q = ChatHistory.query.filter_by(user_id=user_id)
        conv_id = request.args.get('conversation_id')
        if conv_id:
            try:
                q = q.filter_by(conversation_id=int(conv_id))
            except Exception:
                pass
        rows = q.order_by(ChatHistory.created_at.asc()).limit(limit).all()
        out = []
        for r in rows:
            out.append({
                'id': r.id,
                'conversation_id': r.conversation_id,
                'user': r.user_message,
                'ai': r.ai_response,
                'sentiment': {
                    'label': r.sentiment_label,
                    'score': float(r.sentiment_score) if r.sentiment_score is not None else None,
                },
                'created_at': r.created_at.isoformat() if getattr(r, 'created_at', None) else None,
            })
        return jsonify(out), 200
    except Exception as e:
        try:
            db.session.rollback()
        except Exception:
            pass
        return jsonify({'message': str(e)}), 500


@chat_bp.route('/conversations', methods=['GET', 'POST'])
@jwt_required()
def conversations():
    """List user's conversations or create a new one.
    GET: returns [{id, title, updated_at, created_at}]
    POST: {title?} -> creates and returns the conversation
    """
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except Exception:
        pass

    if request.method == 'GET':
        rows = Conversation.query.filter_by(user_id=user_id).order_by(Conversation.updated_at.desc()).all()
        return jsonify([
            {
                'id': r.id,
                'title': r.title,
                'created_at': r.created_at.isoformat() if r.created_at else None,
                'updated_at': r.updated_at.isoformat() if r.updated_at else None,
            } for r in rows
        ]), 200

    data = request.get_json() or {}
    title = (data.get('title') or 'New chat').strip() or 'New chat'
    conv = Conversation(user_id=user_id, title=title)
    db.session.add(conv)
    db.session.commit()
    return jsonify({'id': conv.id, 'title': conv.title, 'created_at': conv.created_at.isoformat(), 'updated_at': conv.updated_at.isoformat()}), 201


@chat_bp.route('/conversations/<int:conv_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def conversation_detail(conv_id):
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except Exception:
        pass

    conv = Conversation.query.filter_by(id=conv_id, user_id=user_id).first()
    if not conv:
        return jsonify({'message': 'Conversation not found'}), 404

    if request.method == 'PUT':
        data = request.get_json() or {}
        new_title = data.get('title')
        if new_title:
            conv.title = new_title.strip() or conv.title
        conv.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'id': conv.id, 'title': conv.title, 'created_at': conv.created_at.isoformat(), 'updated_at': conv.updated_at.isoformat()}), 200

    # DELETE
    db.session.delete(conv)
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200