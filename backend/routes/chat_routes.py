# backend/routes/chat_routes.py
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
pipeline = None
torch = None
genai = None

# We'll suppress model logs only if transformers gets imported during lazy load

# Initialize placeholders for lazy loading
sentiment_pipeline = None
chat_session = None
text_generator = None
_models_loaded = False
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'response_templates.yaml')
response_templates = {}

USE_LOCAL_MODEL = os.getenv('USE_LOCAL_MODEL', 'false').lower() in ('1', 'true', 'yes')
# Default to False for development safety; enable by setting USE_GENAI=1 in your environment
USE_GENAI = os.getenv('USE_GENAI', 'false').lower() in ('1', 'true', 'yes')


def ensure_models_loaded():
    """Load models on first use. This keeps app startup quick and downloads happen only when needed."""
    global sentiment_pipeline, chat_session, text_generator, _models_loaded
    if _models_loaded:
        return
    _models_loaded = True

    # Lazy import transformers/torch if available
    global HAS_TRANSFORMERS, HAS_GENAI, pipeline, torch, genai
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

    # Lazy import Google Generative AI if available
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
                print('❌ GOOGLE_API_KEY not set. Gemini generation will be skipped.')
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
    """Fetches user profile and formats it as a single string for the AI to use as context."""
    context = ""
    try:
        from models import Profile
        profile = Profile.query.filter_by(user_id=user_id).first()
        if profile:
            # Gather all relevant fields, including the new medication history
            profile_data = {
                'Name': profile.name,
                'Age': profile.age,
                'Gender': profile.gender,
                'Health Conditions': profile.health_conditions,
                'Birthmarks': profile.birthmarks,
                'Family Med History': profile.family_medication_history,
                'Previous Med History': profile.previous_medication_history,
                'Response Style': profile.response_style
            }
            # Filter out empty/None values and build context string
            context_parts = []
            for k, v in profile_data.items():
                # Only include fields with actual data
                if v and str(v).strip().lower() not in ('none', 'n/a', ''):
                    context_parts.append(f"{k}: {v}")
            context = " | ".join(context_parts)
    except Exception as e:
        print(f"Error fetching profile context for user {user_id}: {e}")
    return context

def generate_rule_based_response(message, sentiment_label, sentiment_score=None, history_text='', profile_context=''):
    """Generate a response tailored to the sentiment of the user's message, as a fallback."""
    ensure_models_loaded()

    # Build a practical, health-focused response depending on sentiment
    sentiment_label_up = (sentiment_label or 'NEUTRAL').upper()

    # Derive response style from profile_context if provided (e.g. 'Response Style: detailed')
    response_style = 'concise'
    try:
        if 'Response Style: detailed' in profile_context:
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

    # Tone and construction
    if sentiment_label_up.startswith('NEG'):
        empathic = "I'm sorry you're experiencing this — I hear you."
    elif sentiment_label_up.startswith('POS'):
        empathic = "I'm glad to hear some positive signs — let's build on that." 
    else:
        empathic = "Thanks for sharing — I want to help." 

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
            # The ORIGINAL generic fallback goes here, but only if no other rule matched
            main = f"{empathic} {prefix}Could you tell me when this started or how severe it is? A quick detail helps me give a more useful suggestion."

        # append red flag hint concisely
        if red_flags:
            main += f" If you have severe pain, repeated vomiting, or dehydration signs, please seek urgent care."
        main += f" Sentiment: {sentiment_label_up} ({pct}%)"
        return main


def generate_ai_response(message, history_text='', profile_context=''):
    """Generates a short AI response. Priority: Gemini (if configured) -> local generator. Returns None on failure/disabled."""
    ensure_models_loaded()
    
    # Combine profile and history for better context
    full_context = ''
    if profile_context:
        full_context += f"User Profile Context: {profile_context}\n"
    if history_text:
        full_context += f"Recent Chat History:\n{history_text}\n"

    # Construct the final message/prompt for the LLM
    final_prompt = f"{full_context}User Message: {message}. Provide a health-focused, supportive, and context-aware response within one to three sentences. If a remedy is requested, suggest simple home care or refer to professional advice based on severity."

    # Try Gemini if available and enabled
    if chat_session:
        try:
            # Use the AI model with context
            response = chat_session.send_message(final_prompt)
            return getattr(response, 'text', str(response)).strip()
        except Exception as e:
            print('Gemini generation failed:', e)

    # Try local generator if configured
    if text_generator:
        try:
            # Generate a response with increased max_length for quality
            outputs = text_generator(
                final_prompt,
                max_length=150,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                repetition_penalty=1.2,
                no_repeat_ngram_size=3,
                num_return_sequences=1,
            )
            if outputs and isinstance(outputs, list):
                text = outputs[0].get('generated_text') or outputs[0].get('text') or str(outputs[0])
                # Remove the original prompt which the model might echo
                text = text.replace(final_prompt, '').strip()
                # Clean up and keep the first few sentences
                sentences = re.split(r'(?<=[.!?])\s+', text)
                return ' '.join(sentences[:3]).strip()
        except Exception as e:
            print('Local generation failed:', e)

    # Returns None if both models are unavailable or failed. The calling function handles the final fallback.
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

    # 1. Handle Quick Greeting (priority 1) - unchanged logic
    try:
        # Quick greeting detection: if user says 'hi' / 'hello' / 'hey' variants, respond with a short, user-specific greeting
        msg_low = (message or '').strip().lower()
        if msg_low and re.match(r"^\s*(hi+|hello|hey|hiya|hii)\b", message, re.IGNORECASE):
            # try to fetch profile name
            name = None
            try:
                profile = Profile.query.filter_by(user_id=user_id).first()
                if profile and getattr(profile, 'name', None):
                    name = profile.name
            except Exception:
                name = None

            # Generic greeting requested by user
            if name:
                ai_response = f"Hello {name}. How can I help you today?"
            else:
                ai_response = "Hi — how can I help you today?"

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
        # escalate immediately
        try:
            # treat as severe negative
            sentiment_label = 'NEGATIVE'
            sentiment_score = 95.0
            ai_response = (
                "I hear you — it sounds like you're in urgent distress. If you are in immediate danger, please call your local emergency number now (for example, 911 in the US). "
                "If you are able, consider contacting a crisis line or a trusted person nearby. If you'd like, I can provide local helpline numbers or steps to stay safe right now."
            )
            
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


    # 5. Generate Response (The CORE FIX for LLM priority)
    ai_response = None
    
    # CHECK 1: Try AI Model (Gemini or Local) first if either is active
    ensure_models_loaded()
    if chat_session or text_generator:
        try:
            # Call the LLM with full context. It returns a response or None.
            ai_response = generate_ai_response(
                message, 
                history_text=history_text, 
                profile_context=profile_context
            )
        except Exception as e:
            print("Error during AI model call, falling back to rule-based:", e)
            ai_response = None 

    # CHECK 2: If the model response is None, use rule-based fallback
    if ai_response is None:
        # Use rule-based response as the final guaranteed fallback
        ai_response = generate_rule_based_response(
            message, 
            sentiment_label, 
            sentiment_score, 
            history_text, 
            profile_context
        )
    
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