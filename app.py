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

# HR AI Assistant Prompts - GENERIC RESPONSES ONLY
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
    
    Provide specific, actionable advice with examples. Do not reference any specific companies, personal experiences, or proprietary methodologies. Do not say "I" or claim personal experience. Provide objective, research-based guidance.""",
    
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
    
    Provide specific language suggestions and improvements. Do not reference any specific companies or personal experiences. Do not say "I" or claim personal experience. Provide objective, research-based guidance.""",
    
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
    
    Focus on practical, immediately actionable guidance. Do not reference any specific companies or personal experiences. Do not say "I" or claim personal experience. Provide objective, research-based guidance.""",
    
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
    
    Provide data-driven recommendations with clear rationale. Do not reference any specific companies or personal experiences. Do not say "I" or claim personal experience. Provide objective, research-based guidance.""",
    
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
    
    Provide systematic, implementable solutions. Do not reference any specific companies or personal experiences. Do not say "I" or claim personal experience. Provide objective, research-based guidance."""
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

@app.route('/')
@app.route('/demo')
def demo():
    """Landing page with original design"""
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Your AI Talent Strategist</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
            }
            
            .header {
                background: linear-gradient(135deg, #FF9A56 0%, #FF7B3D 100%);
                padding: 40px 20px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            
            .header h1 {
                color: white;
                font-size: 2.5em;
                font-weight: 300;
                letter-spacing: 2px;
            }
            
            .profile-card {
                background: linear-gradient(135deg, #2C3E50 0%, #34495E 100%);
                max-width: 600px;
                margin: -30px auto 40px;
                padding: 40px;
                border-radius: 20px;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            
            .profile-card h2 {
                color: #FF9A56;
                font-size: 2em;
                margin-bottom: 20px;
            }
            
            .profile-card p {
                color: #ECF0F1;
                font-size: 1.1em;
                line-height: 1.6;
                margin-bottom: 30px;
            }
            
            .profile-links {
                display: flex;
                justify-content: center;
                gap: 20px;
                flex-wrap: wrap;
            }
            
            .profile-link {
                background: #FF9A56;
                color: white;
                padding: 12px 30px;
                border-radius: 25px;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            
            .profile-link:hover {
                background: #FF7B3D;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(255, 154, 86, 0.4);
            }
            
            .main-container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 40px 20px;
            }
            
            .section {
                background: white;
                padding: 40px;
                border-radius: 15px;
                margin-bottom: 30px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            }
            
            .section h3 {
                color: #2C3E50;
                font-size: 1.8em;
                margin-bottom: 20px;
                text-align: center;
            }
            
            .focus-area {
                display: flex;
                align-items: center;
                gap: 15px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            
            .focus-icon {
                font-size: 2em;
            }
            
            .focus-text {
                color: #3498DB;
                font-size: 1.3em;
                font-weight: 600;
            }
            
            .challenge-section {
                text-align: center;
            }
            
            .challenge-input {
                width: 100%;
                max-width: 600px;
                padding: 20px;
                font-size: 1em;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                margin: 20px auto;
                display: block;
                resize: vertical;
                min-height: 120px;
            }
            
            .challenge-input:focus {
                outline: none;
                border-color: #FF9A56;
            }
            
            .cta-button {
                background: linear-gradient(135deg, #FF9A56 0%, #FF7B3D 100%);
                color: white;
                padding: 18px 50px;
                font-size: 1.2em;
                border: none;
                border-radius: 30px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 5px 15px rgba(255, 154, 86, 0.3);
            }
            
            .cta-button:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 20px rgba(255, 154, 86, 0.4);
            }
            
            .category-selector {
                margin: 20px 0;
                text-align: center;
            }
            
            .category-selector select {
                padding: 12px 20px;
                font-size: 1em;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background: white;
                cursor: pointer;
            }
            
            .response-box {
                background: #f8f9fa;
                padding: 30px;
                border-radius: 10px;
                margin-top: 30px;
                min-height: 150px;
                border-left: 5px solid #FF9A56;
            }
            
            .response-box.loading {
                text-align: center;
                color: #7f8c8d;
                font-style: italic;
            }
            
            .response-box.active {
                background: white;
                box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            }
            
            @media (max-width: 768px) {
                .header h1 {
                    font-size: 1.8em;
                }
                
                .profile-card {
                    margin: -20px 20px 30px;
                    padding: 30px 20px;
                }
                
                .profile-card h2 {
                    font-size: 1.5em;
                }
                
                .section {
                    padding: 25px 20px;
                }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Your AI Talent Strategist</h1>
        </div>
        
        <div class="profile-card">
            <h2>Triparna Chakraborty</h2>
            <p>Engineer-turned-HRBP | 12+ Years Global Experience | People Partner</p>
            <div class="profile-links">
                <a href="https://www.linkedin.com/in/triparna-chakraborty/" target="_blank" class="profile-link">LinkedIn</a>
                <a href="mailto:triparna.chakraborty@example.com" class="profile-link">Contact</a>
            </div>
        </div>
        
        <div class="main-container">
            <div class="section">
                <h3>Strategic Focus Area:</h3>
                <div class="focus-area">
                    <span class="focus-icon">🎯</span>
                    <span class="focus-text">Hiring & Workforce Planning</span>
                </div>
            </div>
            
            <div class="section challenge-section">
                <h3>Your Strategic People Challenge:</h3>
                <p style="color: #7f8c8d; margin-bottom: 20px;">
                    Describe your organizational challenge or strategic question. I'll provide data-driven insights.
                </p>
                
                <div class="category-selector">
                    <label for="category" style="font-weight: 600; margin-right: 10px;">Select Category:</label>
                    <select id="category">
                        <option value="workforce_planning">Workforce Planning</option>
                        <option value="interview_design">Interview Design</option>
                        <option value="job_descriptions">Job Descriptions</option>
                        <option value="leadership_coaching">Leadership Coaching</option>
                        <option value="hr_systems">HR Systems</option>
                    </select>
                </div>
                
                <textarea 
                    id="challengeInput" 
                    class="challenge-input" 
                    placeholder="Example: We're scaling from 50 to 200 employees in 12 months. How should we structure our hiring roadmap?"
                ></textarea>
                
                <button class="cta-button" onclick="getStrategicGuidance()">
                    Get Strategic Guidance
                </button>
                
                <div id="responseBox" class="response-box">
                    <em style="color: #95a5a6;">Your AI-powered guidance will appear here...</em>
                </div>
            </div>
        </div>
        
        <script>
        async function getStrategicGuidance() {
            const input = document.getElementById('challengeInput').value;
            const category = document.getElementById('category').value;
            const responseBox = document.getElementById('responseBox');
            
            if (!input.trim()) {
                alert('Please describe your challenge or question.');
                return;
            }
            
            responseBox.className = 'response-box loading';
            responseBox.innerHTML = '<em>Analyzing your challenge and generating insights...</em>';
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: input,
                        category: category,
                        session_id: 'web-session-' + Date.now()
                    })
                });
                
                const data = await response.json();
                
                responseBox.className = 'response-box active';
                responseBox.innerHTML = '<strong>Strategic Guidance:</strong><br><br>' + 
                    data.response.replace(/\n/g, '<br>');
                    
            } catch (error) {
                responseBox.className = 'response-box';
                responseBox.innerHTML = '<em style="color: #e74c3c;">Error: Unable to generate guidance. Please try again.</em>';
            }
        }
        
        document.getElementById('challengeInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                getStrategicGuidance();
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
    
    print(f"🚀 Starting Your AI Talent Strategist on port {port}")
    print(f"🌐 Access at: http://localhost:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
