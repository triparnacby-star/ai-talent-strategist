import os
from flask import Flask, request, jsonify, render_template_string
from anthropic import Anthropic
from dotenv import load_dotenv
from flask_cors import CORS
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple analytics storage (in production, use a database)
analytics_data = {
    "total_queries": 0,
    "category_usage": {},
    "start_time": datetime.now()
}

# HTML template with Anthropic-inspired design and correct sidebar layout
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your AI People Partner</title>
    
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'GA_MEASUREMENT_ID');
        
        function trackQuery(category) {
            gtag('event', 'hr_query', {
                'event_category': 'People Partner Assistant',
                'event_label': category,
                'value': 1
            });
        }
    </script>
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            min-height: 100vh;
            padding: 20px;
            color: #334155;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 24px;
            box-shadow: 
                0 25px 50px -12px rgba(0, 0, 0, 0.15),
                0 0 0 1px rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #ff6b35 0%, #ff8c42 100%);
            color: white;
            padding: 16px 40px;
            text-align: center;
            position: relative;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
            pointer-events: none;
        }
        
        .header h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 16px;
            position: relative;
            z-index: 1;
            letter-spacing: -0.025em;
        }
        
        .header .tagline {
            font-size: 1.25rem;
            opacity: 0.95;
            font-weight: 400;
            margin-bottom: 24px;
            position: relative;
            z-index: 1;
        }
        
        .brand-message {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px 32px;
            border-radius: 16px;
            margin: 32px auto 0;
            max-width: 700px;
            position: relative;
            z-index: 1;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .brand-message p {
            font-size: 1.1rem;
            font-weight: 500;
            margin: 0;
        }
        
        .main-content {
            padding: 48px 40px;
        }
        
        .content-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 40px;
            align-items: start;
        }
        
        .form-section {
            background: #f8fafc;
            padding: 32px;
            border-radius: 20px;
            border: 1px solid #e2e8f0;
        }
        
        .sidebar {
            position: sticky;
            top: 20px;
        }
        
        .creator-info {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            padding: 24px;
            border-radius: 16px;
            color: white;
            text-align: center;
        }
        
        .creator-info h3 {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 12px;
            color: #ff8c42;
        }
        
        .creator-info p {
            margin: 8px 0 16px 0;
            opacity: 0.9;
            font-size: 0.95rem;
        }
        
        .creator-info .links {
            display: flex;
            justify-content: center;
            gap: 16px;
        }
        
        .creator-info a {
            color: #ff8c42;
            text-decoration: none;
            font-weight: 500;
            font-size: 0.9rem;
            transition: all 0.2s ease;
        }
        
        .creator-info a:hover {
            color: #ff6b35;
            text-decoration: underline;
        }
        
        .form-group {
            margin-bottom: 24px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 12px;
            font-weight: 600;
            color: #1e293b;
            font-size: 1.1rem;
        }
        
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 16px 20px;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            font-size: 16px;
            font-family: inherit;
            transition: all 0.2s ease;
            background: white;
        }
        
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #ff6b35;
            box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
        }
        
        .form-group textarea {
            min-height: 120px;
            resize: vertical;
        }
        
        .button-group {
            display: flex;
            gap: 16px;
            margin: 24px 0;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 16px 32px;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            flex: 1;
            min-width: 160px;
            font-family: inherit;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #ff6b35 0%, #ff8c42 100%);
            color: white;
            box-shadow: 0 4px 14px 0 rgba(255, 107, 53, 0.3);
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px 0 rgba(255, 107, 53, 0.4);
        }
        
        .btn-secondary {
            background: #64748b;
            color: white;
            box-shadow: 0 4px 14px 0 rgba(100, 116, 139, 0.3);
        }
        
        .btn-secondary:hover {
            background: #475569;
            transform: translateY(-2px);
        }
        
        .examples-section {
            margin: 32px 0;
        }
        
        .examples-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
        }
        
        .example-card {
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 16px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.2s ease;
            text-align: center;
        }
        
        .example-card:hover {
            border-color: #ff6b35;
            box-shadow: 0 8px 25px 0 rgba(255, 107, 53, 0.1);
            transform: translateY(-2px);
        }
        
        .example-card .icon {
            font-size: 2rem;
            margin-bottom: 12px;
        }
        
        .example-card h4 {
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 8px;
        }
        
        .example-card p {
            font-size: 0.9rem;
            color: #64748b;
            margin: 0;
        }
        
        .response-area {
            margin-top: 32px;
            padding: 32px;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-radius: 20px;
            border-left: 4px solid #ff6b35;
            display: none;
        }
        
        .response-area.active {
            display: block;
        }
        
        .response-area h4 {
            color: #1e293b;
            margin-bottom: 16px;
            font-size: 1.25rem;
            font-weight: 600;
        }
        
        .loading {
            text-align: center;
            color: #ff6b35;
            font-style: italic;
            font-size: 1.1rem;
        }
        
        .error {
            color: #dc2626;
            background: #fef2f2;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #fecaca;
        }
        
        .success {
            color: #1e293b;
            background: white;
            padding: 24px;
            border-radius: 12px;
            white-space: pre-wrap;
            line-height: 1.7;
            border: 1px solid #e2e8f0;
        }
        
        .analytics-display {
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            padding: 16px 24px;
            border-radius: 12px;
            margin-top: 24px;
            font-size: 0.9rem;
            color: #1e40af;
            text-align: center;
            display: none;
        }
        
        .footer {
            text-align: center;
            padding: 40px;
            background: #f8fafc;
            color: #64748b;
            border-top: 1px solid #e2e8f0;
        }
        
        .footer h4 {
            color: #1e293b;
            margin-bottom: 12px;
            font-weight: 600;
        }
        
        .tech-stack {
            margin: 16px 0;
            font-size: 0.85rem;
            opacity: 0.8;
        }
        
        @media (max-width: 768px) {
            .container {
                margin: 10px;
                border-radius: 16px;
            }
            
            .header {
                padding: 32px 24px;
            }
            
            .header h1 {
                font-size: 1.5rem;
            }
            
            .main-content {
                padding: 32px 24px;
            }
            
            .content-grid {
                grid-template-columns: 1fr;
                gap: 24px;
            }
            
            .sidebar {
                order: -1;
                position: static;
            }
            
            .creator-info {
                padding: 20px;
            }
            
            .creator-info .links {
                flex-direction: column;
                gap: 8px;
            }
            
            .button-group {
                flex-direction: column;
            }
            
            .examples-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Your AI Talent Strategist</h1>
        </div>
        
        <div class="main-content">
            <div class="content-grid">
                <div class="form-section">
                    <form id="hrForm">
                        <div class="form-group">
                            <label for="category">Strategic Focus Area:</label>
                            <select id="category" name="category">
                                <option value="hiring_workforce_planning">🎯 Hiring & Workforce Planning</option>
                                <option value="job_descriptions">📝 Job Descriptions & Talent Marketing</option>
                                <option value="leadership">👥 Leadership Development & Coaching</option>
                                <option value="performance_management">📊 Performance Management & OKRs</option>
                                <option value="systems">⚙️ HR Systems & Process Design</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="question">Your Strategic People Challenge:</label>
                            <textarea id="question" name="question" placeholder="Describe your organizational challenge or strategic question. I'll provide data-driven insights and actionable frameworks based on proven methodologies from scaling high-performance teams..."></textarea>
                        </div>
                        
                        <div class="button-group">
                            <button type="button" class="btn btn-primary" onclick="sendMessage()">Get Strategic Guidance</button>
                            <button type="button" class="btn btn-secondary" onclick="clearForm()">Clear</button>
                        </div>
                    </form>
                
                    <div class="examples-section">
                        <div class="examples-grid">
                            <div class="example-card" onclick="loadExample('hiring_workforce_planning')">
                                <div class="icon">🎯</div>
                                <h4>Workforce Planning</h4>
                                <p>Strategic hiring roadmaps for AI infrastructure teams</p>
                            </div>
                            <div class="example-card" onclick="loadExample('job_descriptions')">
                                <div class="icon">📝</div>
                                <h4>Talent Marketing</h4>
                                <p>Bias-free job descriptions that attract top technical talent</p>
                            </div>
                            <div class="example-card" onclick="loadExample('leadership')">
                                <div class="icon">👥</div>
                                <h4>Executive Coaching</h4>
                                <p>Leadership frameworks for scaling technical organizations</p>
                            </div>
                        </div>
                    </div>
                    
                    <div id="responseArea" class="response-area">
                        <div id="responseContent"></div>
                    </div>
                    
                    <div class="analytics-display" id="analyticsDisplay">
                        <strong>Session Analytics:</strong> <span id="analyticsText"></span>
                    </div>
                </div>
                
                <div class="sidebar">
                    <div class="creator-info">
                        <h3>Triparna Chakraborty</h3>
                        <p>Engineer-turned-HRBP | 12+ Years Global Experience | People Partner</p>
                        <div class="links">
                            <a href="https://linkedin.com/in/triparnachakraborty" target="_blank">LinkedIn</a>
                            <a href="mailto:triparna.cby@gmail.com">Contact</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <h4>Your AI Talent Strategist</h4>
            <p>Built by an Engineer-turned-HR Partner who uses data modeling to create high-performance organizations</p>
            <div class="tech-stack">
                Powered by Claude AI • Built with Engineering Precision • Designed for Scale
            </div>
            <p style="margin-top: 16px;">© 2025 Triparna Chakraborty. Engineered for the future of work.</p>
        </div>
    </div>

    <script>
        let sessionQueries = 0;
        let sessionStartTime = new Date();
        
        function updateAnalytics() {
            const analyticsDisplay = document.getElementById('analyticsDisplay');
            const analyticsText = document.getElementById('analyticsText');
            
            if (sessionQueries > 0) {
                const duration = Math.round((new Date() - sessionStartTime) / 1000);
                analyticsText.textContent = `${sessionQueries} strategic consultations • ${duration}s session time`;
                analyticsDisplay.style.display = 'block';
            }
        }
        
        function loadExample(type) {
            const examples = {
                hiring_workforce_planning: "We're launching GenAI infrastructure in 6 months. What roles should we hire now and in what sequence to ensure successful delivery?",
                job_descriptions: "Help me create a bias-free job description for a Senior ML Engineer that attracts diverse candidates while highlighting growth opportunities",
                leadership: "How do I provide effective feedback to a high-performing technical lead who is creating team friction?"
            };
            
            document.getElementById('question').value = examples[type];
            document.getElementById('category').value = type;
            
            if (typeof gtag !== 'undefined') {
                gtag('event', 'example_loaded', {
                    'event_category': 'User Interaction',
                    'event_label': type
                });
            }
        }
        
        function clearForm() {
            document.getElementById('question').value = '';
            document.getElementById('category').value = 'hiring_workforce_planning';
            document.getElementById('responseArea').classList.remove('active');
        }
        
        function sendMessage() {
            const question = document.getElementById('question').value.trim();
            const category = document.getElementById('category').value;
            
            if (!question) {
                alert('Please describe your strategic challenge');
                return;
            }
            
            sessionQueries++;
            updateAnalytics();
            
            if (typeof gtag !== 'undefined') {
                trackQuery(category);
            }
            
            const responseArea = document.getElementById('responseArea');
            const responseContent = document.getElementById('responseContent');
            
            responseArea.classList.add('active');
            responseContent.innerHTML = '<div class="loading">🔍 Analyzing your challenge and developing strategic recommendations...</div>';
            
            const startTime = new Date();
            
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: question,
                    category: category
                })
            })
            .then(response => response.json())
            .then(data => {
                const responseTime = new Date() - startTime;
                
                if (data.error) {
                    responseContent.innerHTML = `<div class="error">❌ ${data.error}</div>`;
                } else {
                    responseContent.innerHTML = `
                        <div class="success">
                            <h4>🎯 Strategic Recommendations:</h4>
                            ${data.response}
                            
                            <div style="margin-top: 20px; padding-top: 16px; border-top: 1px solid #e2e8f0; font-size: 0.9em; color: #64748b;">
                                <em>Analysis completed in ${responseTime}ms • Powered by data-driven methodologies</em>
                            </div>
                        </div>`;
                }
                
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'response_received', {
                        'event_category': 'Performance',
                        'event_label': category,
                        'value': responseTime
                    });
                }
            })
            .catch(error => {
                responseContent.innerHTML = `<div class="error">❌ Connection error. Please check if the server is running.</div>`;
            });
        }
        
        if (typeof gtag !== 'undefined') {
            gtag('event', 'page_view', {
                'event_category': 'Engagement',
                'event_label': 'AI People Partner Loaded'
            });
        }
    </script>
</body>
</html>
'''

def generate_response(message, category):
    """Generate HR advice using Claude with enhanced context"""
    
    # Track analytics
    analytics_data["total_queries"] += 1
    if category in analytics_data["category_usage"]:
        analytics_data["category_usage"][category] += 1
    else:
        analytics_data["category_usage"][category] = 1
    
    # Enhanced prompt engineering aligned with Triparna's background
    base_prompts = {
        "hiring_workforce_planning": """You are Triparna Chakraborty, an Engineer-turned-People Partner with 12+ years of experience scaling organizations globally. You've led Strategic Workforce Planning 2030 for 3,000+ employees at Genentech, implemented AI modeling for talent analysis, and reduced executive hiring time by 50% in international markets.

Your expertise includes:
- Strategic Workforce Planning using AI modeling and competitive intelligence
- Scaling teams across 40+ countries with diverse regulatory environments
- Engineering background that helps you understand technical team dynamics
- Data-driven approaches to organizational design and talent strategy

FOR WORKFORCE PLANNING QUESTIONS:
IMMEDIATE ROLES & SEQUENCING:
- Specific job titles with levels based on your Genentech experience
- Critical path analysis for role dependencies
- Budget considerations and fully-loaded costs
- Realistic timelines based on current market conditions

ORGANIZATIONAL DESIGN:
- Team ratios proven at scale (your experience with 3,000+ teams)
- Reporting structures that minimize overhead
- Cross-functional collaboration patterns
- Performance management alignment

MARKET INTELLIGENCE:
- Salary benchmarking using competitive intelligence methods
- Talent availability and hiring difficulty by role
- Alternative sourcing strategies beyond traditional channels
- Retention strategies for high-performers

Provide specific, actionable recommendations with implementation timelines.""",

        "job_descriptions": """You are Triparna Chakraborty, an Engineer-turned-People Partner who has transformed global recruitment strategies across multiple markets. You've created bias-free hiring frameworks that reduced time-to-fill by 50% and built inclusive talent marketing strategies across 40+ countries.

Your approach emphasizes:
- Engineering precision in language and requirements
- Data-driven talent marketing that converts
- Global perspective on inclusive hiring practices
- Technical credibility for engineering roles

FOR JOB DESCRIPTION OPTIMIZATION:
STRUCTURE & LANGUAGE:
- Remove bias-inducing language based on your global experience
- Clear technical requirements vs. nice-to-haves
- Growth trajectories that appeal to ambitious candidates
- Compensation transparency aligned with market data

TECHNICAL ROLES:
- Engineering background helps you write credible technical JDs
- Stack-specific details that resonate with engineers
- Career progression paths for technical talent
- Culture elements that attract diverse technical talent

GLOBAL CONSIDERATIONS:
- Language that works across diverse markets
- Regulatory compliance for different regions
- Cultural adaptation strategies
- Remote work considerations

Provide before/after examples and specific templates they can implement immediately.""",

        "leadership": """You are Triparna Chakraborty, an Engineer-turned-People Partner who has coached senior leaders through major organizational transformations at Genentech and Roche. You've guided managers through complex workforce changes including 6% headcount reductions and provided executive coaching during high-stakes restructuring.

Your coaching methodology combines:
- Engineering problem-solving approach to leadership challenges
- Proven frameworks from scaling 3,000+ person organizations
- Global perspective from managing across diverse cultures
- Data-driven performance management strategies

FOR LEADERSHIP DEVELOPMENT:
DIFFICULT CONVERSATIONS:
- SBI-I framework with specific scripts
- De-escalation techniques proven in high-stress environments
- Documentation strategies for legal compliance
- Follow-up frameworks to ensure sustainable change

PERFORMANCE MANAGEMENT:
- OKR alignment strategies for technical teams
- Calibration processes for consistent evaluation
- Career development frameworks for different tracks
- Succession planning for critical roles

ORGANIZATIONAL EFFECTIVENESS:
- Change management communication strategies
- Team dynamics optimization for technical teams
- Meeting efficiency and decision-making frameworks
- Culture building during rapid scaling

Provide specific templates, scripts, and step-by-step implementation guides.""",

        "performance_management": """You are Triparna Chakraborty, an Engineer-turned-People Partner who has designed and implemented performance management systems for organizations scaling from hundreds to thousands of employees. You've conducted talent reviews, succession planning, and performance calibration sessions with VPs and senior leaders.

Your systematic approach includes:
- Data-driven performance evaluation methods
- AI modeling for succession planning and talent gap analysis
- Global performance management across diverse regulatory environments
- Engineering mindset applied to people processes

FOR PERFORMANCE SYSTEMS:
FRAMEWORK DESIGN:
- OKR structures adapted for different organizational levels
- Performance rating scales that drive differentiation
- Calibration processes that ensure fairness
- Documentation requirements for compliance

TALENT REVIEWS:
- Succession planning methodologies using data analysis
- High-potential identification and development programs
- Performance improvement plan templates that work
- Career development frameworks for technical and business tracks

SCALING CONSIDERATIONS:
- Manager training curricula for consistent execution
- Performance review cycles optimized for business needs
- Compensation review alignment with performance outcomes
- Global considerations for multinational organizations

Provide implementation roadmaps, templates, and success metrics.""",

        "systems": """You are Triparna Chakraborty, an Engineer-turned-People Partner who has led global HR transformation projects including designing the first digital onboarding experience for 20,000+ employees across 40+ countries. You've implemented Workday systems, created scalable processes, and built HR technology solutions.

Your systems expertise includes:
- Global HRIS implementation and optimization
- Process design with engineering precision
- Change management for technology adoption
- Cross-functional project leadership

FOR HR SYSTEMS DESIGN:
TECHNOLOGY ARCHITECTURE:
- HRIS selection criteria based on organizational scale
- Integration requirements for seamless employee experience
- Data flow optimization for people analytics
- Security and compliance considerations

PROCESS OPTIMIZATION:
- Onboarding workflows that improve productivity and belonging
- Performance management process automation
- Recruitment technology stack optimization
- Employee self-service design principles

GLOBAL SCALABILITY:
- Multi-country deployment strategies
- Local compliance integration
- Cultural adaptation frameworks
- Change management for global rollouts

Provide technical specifications, implementation timelines, and vendor evaluation frameworks."""
    }
    
    # Get the appropriate system prompt
    system_prompt = base_prompts.get(category, base_prompts["hiring_workforce_planning"])
    
    # Enhanced context for better responses
    enhanced_prompt = f"""{system_prompt}

Context: You are consulting with a leader who needs strategic people guidance. Draw from your specific experience at Genentech, Roche, and global organizations to provide concrete, actionable advice.

User Question: {message}

Provide a detailed response that includes:
1. Direct answer based on your proven methodologies
2. Specific examples from your experience where relevant
3. Implementation steps with timelines
4. Potential challenges and mitigation strategies
5. Success metrics and tracking methods

Be practical, data-driven, and leverage your unique engineering + HR perspective."""

    try:
        # Initialize Anthropic client
        client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        # Generate response using Claude
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            system=enhanced_prompt,
            messages=[{"role": "user", "content": message}]
        )
        
        return response.content[0].text
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return f"I apologize, but I encountered an error while processing your request. Please ensure your API connection is configured correctly."

@app.route('/')
def home():
    return jsonify({
        "message": "Your AI People Partner is running!", 
        "status": "active",
        "creator": "Triparna Chakraborty - Engineer-turned-People Partner",
        "analytics": analytics_data
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy", 
        "service": "Your AI People Partner",
        "uptime_seconds": (datetime.now() - analytics_data["start_time"]).total_seconds(),
        "total_consultations": analytics_data["total_queries"]
    })

@app.route('/analytics')
def analytics():
    return jsonify({
        **analytics_data,
        "creator": "Triparna Chakraborty",
        "specialization": "Engineer-turned-People Partner",
        "experience": "12+ years global HR experience"
    })

@app.route('/demo')
def demo():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle strategic consultation requests"""
    try:
        data = request.json
        message = data.get('message', '')
        category = data.get('category', 'hiring_workforce_planning')
        
        if not message:
            return jsonify({'error': 'Please describe your strategic challenge'}), 400
            
        # Generate response using Claude
        response = generate_response(message, category)
        
        return jsonify({
            'response': response,
            'category': category,
            'timestamp': datetime.now().isoformat(),
            'consultant': 'Triparna Chakraborty',
            'session_queries': analytics_data["total_queries"]
        })
        
    except Exception as e:
        logger.error(f"Error in consultation endpoint: {str(e)}")
        return jsonify({'error': 'Unable to process consultation request'}), 500

if __name__ == '__main__':
    print("🚀 Starting Your AI Talent Strategist")
    print("👤 Created by: Triparna Chakraborty")
    print("🎯 Specialization: Engineer-turned-HR Partner")
    print("🏥 Health check: http://localhost:5000/health")
    print("📈 Analytics: http://localhost:5000/analytics")
    print("💬 API endpoint: http://localhost:5000/chat")
    print("🔬 Data-driven people strategies for high-performance organizations")
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))