    cleaned_text = re.sub(r'```$', '', cleaned_text, flags=re.MULTILINE)
    cleaned_text = cleaned_text.strip()
    
    try:
        return json.loads(cleaned_text)
    except Exception as e:
        print(f"⚠️ [Agent Coder] Parsing failed. Raw text: {text[:100]}...")
        return None

def execute_task_logic(task_title, model=None):
    """
    מצב ביצוע: מנחה את ה-AI לכתוב קוד עבור המשימה ולייצר קובץ אמיתי בתיקייה.
    """
    target_model = model if model else os.getenv("MODEL", "anthropic/claude-3.5-sonnet")
    
    print(f"🤖 [Agent Coder] מתחיל לכתוב קוד עבור: '{task_title}'")
    
    prompt = f"""
    You are the Root Agentic OS, an autonomous AI developer.
    The user has approved the following task from the roadmap: "{task_title}".
    
    Your job is to generate the working code to fulfill this task.
    Return your response STRICTLY as a JSON object with no additional formatting.
    The JSON must contain two keys:
    1. "file_path": The path where the file should be saved (e.g., "core/new_feature.py").
    2. "content": The actual code to be written into that file.
    """
    
    try:
        response = client.chat.completions.create(
            model=target_model,
            messages=[
                {"role": "system", "content": "You output strict JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"} 
        )
        
        raw_content = response.choices[0].message.content
        result = clean_json_response(raw_content)
        
        if not result:
            return False, "ה-AI החזיר מבנה נתונים לא תקין"

        file_path = result.get("file_path", f"auto_generated_{int(time.time())}.py")
        content = result.get("content", "")
        
        # הגנה: מונע כתיבה מחוץ לתיקיית הפרויקט
        full_path = os.path.abspath(os.path.join(PROJECT_ROOT, file_path))
        if not full_path.startswith(PROJECT_ROOT):
            raise Exception("Security Error: Attempt to write outside project directory.")
            
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return True, file_path
        
    except Exception as e:
        return False, str(e)


def generate_roadmap_strategy(idea, model=None):
    """
    מצב ארכיטקט: הופך רעיון חופשי מהצאט לרשימת משימות מסודרת.
    """
    target_model = model if model else os.getenv("MODEL", "anthropic/claude-3.5-sonnet")
    
    print(f"🧬 [Agent Architect] מנתח את הרעיון: '{idea}'...")
    
    prompt = f"""
    You are the Root OS Strategic Architect. 
    The user has submitted a new idea via chat: "{idea}"
    
    Break this idea down into a structured development roadmap.
    Return your response STRICTLY as a JSON object with one key: "tasks".
    "tasks" should be a list of strings, where each string is a clear, actionable dev task.
    Limit the roadmap to 3-6 essential tasks.
    """
    
    try:
        response = client.chat.completions.create(
            model=target_model,
            messages=[
                {"role": "system", "content": "You output strict JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        raw_content = response.choices[0].message.content
        result = clean_json_response(raw_content)
        
        if result and "tasks" in result:
             return True, result["tasks"]
        else:
             return False, "ה-AI לא הצליח לחלץ משימות מהרעיון."
             
    except Exception as e:
        return False, str(e)