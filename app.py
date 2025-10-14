import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from anthropic import Anthropic
from dotenv import load_dotenv
import logging
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Anthropic client
anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HR AI Assistant Prompts - COMPLETELY GENERIC
HR_SYSTEM_PROMPTS = {
    "interview_design": """You are an HR AI assistant specializing in inclusive, bias-free interview design. 
    Your capabilities include:
    - Structured behavioral interview techniques
    - Bias mitigation strategies
    - Question banks for different roles
    - Rubric creation and calibration
    - Interview process optimization
    
    Always prioritize:
    1. Inclusive practices that minimize bias
    2. Structured, consistent evaluation criteria  
    3. Legal compliance and best practices
    4. Practical implementation guidance
    
    Provide specific, actionable advice with examples. Do not reference any specific companies, personal experiences, or proprietary methodologies.""",
    
    "job_descriptions": """You are an HR AI assistant focused on creating equitable, compelling job descriptions that attract diverse talent.
    Your capabilities include:
    - Inclusive language analysis
    - Requirements optimization (must-have vs nice-to-have)
    - Best practice recommendations
    - Accessibility considerations
    - Industry-standard approaches
    
    Always focus on:
    1. Reducing gendered or biased language
    2. Clear, realistic requirements
    3. Compelling value propositions
    4. Accessibility considerations
    5. Legal compliance
    
    Provide specific language suggestions and improvements. Do not reference any specific companies or personal experiences.""",
    
    "leadership_coaching": """You are an HR AI assistant specializing in people leadership guidance.
    Your capabilities include:
    - Difficult conversation frameworks
    - Performance management strategies
    - Team dynamics and conflict resolution
    - Meeting optimization techniques
    - Culture building approaches
    
    Always provide:
    1. Specific conversation frameworks
    2. Multiple scenario approaches
    3. Balanced, professional advice
    4. Follow-up recommendations
    5. Best practice guidance
    
    Focus on practical, immediately actionable guidance. Do not reference any specific companies, personal experiences, or proprietary methodologies.""",
    
    "workforce_planning": """You are an HR AI assistant focused on strategic workforce planning.
    Your capabilities include:
    - Headcount modeling approaches
    - Role prioritization frameworks
    - Budget planning strategies  
    - Skills gap analysis
    - Organizational design principles
    
    Always consider:
    1. Stage-appropriate hiring strategies
    2. Evaluation frameworks
    3. Team structure optimization
    4. Remote/hybrid workforce considerations
    5. Cost-effective scaling approaches
    
    Provide data-driven recommendations with clear rationale. Do not reference any specific companies or personal experiences.""",
    
    "hr_systems": """You are an HR AI assistant specializing in scalable HR systems and operations.
    Your capabilities include:
    - Onboarding process design
    - Performance review frameworks
    - Employee lifecycle management
    - Compliance considerations
    - HR technology optimization
    
    Always focus on:
    1. Scalable, efficient processes
    2. Compliance and risk management
    3. Employee experience optimization
    4. Data-driven insights and metrics
    5. Technology integration strategies
    
    Provide systematic, implementable solutions. Do not reference any specific companies or personal experiences."""
}

def get_hr_response(category, user_message, conversation_history=None):
    """Generate HR AI assistant response using Claude"""
    
    system_prompt = HR_SYSTEM_PROMPTS.get(category, HR_SYSTEM_PROMPTS["leadership_coaching"])
    
    # Build conversation context
    messages = []
    
    if conversation_history:
        for msg in conversation_history[-6:]:  # Last 6 messages for context
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    
    messages.append({
        "role": "user", 
        "content": user_message
    })
    
    try:
        response = anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            system=system_prompt,
            messages=messages
        )
        
        return response.content[0].text
        
    except Exception as e:
        logger.error(f"Error getting Claude response: {str(e)}")
        return f"I apologize, but I'm having trouble processing your request right now. Please try again in a moment."

# In-memory session storage (in production, use Redis or database)
sessions = {}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        
        user_message = data['message']
        category = data.get('category', 'leadership_coaching')
        session_id = data.get('session_id', 'default')
        
        # Get or create session
        if session_id not in sessions:
            sessions[session_id] = []
        
        # Get AI response
        response_text = get_hr_response(
            category=category,
            user_message=user_message,
            conversation_history=sessions[session_id]
        )
        
        # Store conversation
        sessions[session_id].append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        sessions[session_id].append({
            "role": "assistant", 
            "content": response_text,
            "category": category,
            "timestamp": datetime.now().isoformat()
        })
        
        return jsonify({
            "response": response_text,
            "category": category,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/categories', methods=['GET'])
def get_categories():
    """Get available HR categories"""
    categories = {
        "interview_design": "Inclusive Interview Design",
        "job_descriptions": "Equitable Job Descriptions", 
        "leadership_coaching": "Leadership Coaching",
        "workforce_planning": "Strategic Workforce Planning",
        "hr_systems": "Scalable HR Systems"
    }
    return jsonify(categories)

@app.route('/demo', methods=['GET'])
def demo():
    """Simple demo interface - GENERIC VERSION"""
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI HR Assistant Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 8px; }
            .chat-box { background: white; padding: 15px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .user-msg { background: #e3f2fd; }
            .ai-msg { background: #f3e5f5; }
            input[type="text"] { width: 70%; padding: 10px; margin: 5px; }
            button { padding: 10px 20px; margin: 5px; background: #1976d2; color: white; border: none; border-radius: 4px; cursor: pointer; }
            select { padding: 10px; margin: 5px; }
            #response { min-height: 100px; }
        </style>
    </head>
    <body>
        <h1>🤖 AI HR Assistant - Demo</h1>
        
        <div class="container">
            <h2>Test the AI HR Assistant</h2>
            
            <div>
                <select id="category">
                    <option value="interview_design">Inclusive Interview Design</option>
                    <option value="job_descriptions">Equitable Job Descriptions</option>
                    <option value="leadership_coaching">Leadership Coaching</option>
                    <option value="workforce_planning">Strategic Workforce Planning</option>
                    <option value="hr_systems">Scalable HR Systems</option>
                </select>
            </div>
            
            <div>
                <input type="text" id="messageInput" placeholder="Ask your HR question..." />
                <button onclick="sendMessage()">Send</button>
            </div>
            
            <div id="response" class="chat-box ai-msg">
                <em>Your AI response will appear here...</em>
            </div>
        </div>
        
        <div class="container">
            <h3>Quick Test Examples:</h3>
            <button onclick="testMessage('How do I design bias-free interview questions for a Senior Engineer role?')">Interview Questions</button>
            <button onclick="testMessage('Review this job description for inclusive language: Senior Product Manager, 5+ years required')">Job Description Review</button>  
            <button onclick="testMessage('How do I give feedback to a high performer who is creating team tension?')">Difficult Conversation</button>
        </div>

        <script>
        function sendMessage() {
            const message = document.getElementById('messageInput').value;
            const category = document.getElementById('category').value;
            
            if (!message) return;
            
            document.getElementById('response').innerHTML = '<em>Thinking...</em>';
            
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    category: category,
                    session_id: 'demo-session'
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('response').innerHTML = 
                    '<strong>Category:</strong> ' + data.category + '<br/><br/>' +
                    '<strong>Response:</strong><br/>' + data.response.replace(/\\n/g, '<br/>');
            })
            .catch(error => {
                document.getElementById('response').innerHTML = '<em>Error: ' + error + '</em>';
            });
            
            document.getElementById('messageInput').value = '';
        }
        
        function testMessage(msg) {
            document.getElementById('messageInput').value = msg;
            sendMessage();
        }
        
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_template)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"🚀 Starting AI HR Assistant on port {port}")
    print(f"📊 Demo interface: http://localhost:{port}/demo")
    print(f"🏥 Health check: http://localhost:{port}/health")
    print(f"💬 API endpoint: http://localhost:{port}/chat")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
