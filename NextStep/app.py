from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, os, json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'nextstep_secret_key_2024'
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DB = 'nextstep.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, degree TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER, interests TEXT, subjects TEXT,
                skills TEXT, personality TEXT, domain TEXT
            );
            CREATE TABLE IF NOT EXISTS resume_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER, score INTEGER, suggestions TEXT
            );
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER, short_term TEXT, long_term TEXT, progress INTEGER DEFAULT 0
            );
        ''')

DOMAIN_RULES = {
    'Data Science': {'interests': ['Artificial Intelligence','Data Analysis'], 'skills': ['Python','Machine Learning','Data Visualization','SQL'], 'subjects': ['Machine Learning','Statistics','Database Management Systems']},
    'Artificial Intelligence': {'interests': ['Artificial Intelligence','Robotics'], 'skills': ['Python','Machine Learning'], 'subjects': ['Artificial Intelligence','Machine Learning']},
    'Cybersecurity': {'interests': ['Cybersecurity'], 'skills': ['Linux','Networking','Python'], 'subjects': ['Computer Networks','Operating Systems']},
    'Web Development': {'interests': ['Web Development','Coding and Software Development'], 'skills': ['HTML','CSS','JavaScript','API Development'], 'subjects': ['Database Management Systems']},
    'Mobile App Development': {'interests': ['Mobile App Development'], 'skills': ['Java','JavaScript'], 'subjects': ['Operating Systems']},
    'UI/UX Design': {'interests': ['Graphic Design','Product Design'], 'skills': ['UI/UX Design','Figma'], 'subjects': []},
    'Cloud Engineering': {'interests': ['Cloud Computing'], 'skills': ['Cloud Platforms','Linux','API Development'], 'subjects': ['Computer Networks','Operating Systems']},
    'Internet of Things': {'interests': ['Internet of Things','Robotics'], 'skills': ['C++','Python','Networking'], 'subjects': ['Embedded Systems','Electronics','Digital Logic']},
    'Software Development': {'interests': ['Coding and Software Development'], 'skills': ['Python','Java','C++','Git and GitHub'], 'subjects': ['Data Structures','Algorithms','Operating Systems']},
    'Product Management': {'interests': ['Business Strategy','Product Design'], 'skills': ['UI/UX Design'], 'subjects': ['Database Management Systems']},
}

ROADMAPS = {
    'Data Science': {
        'steps': [
            {'title': 'Learn Python Basics', 'subtopics': ['Variables','Data Types','Conditional Statements','Loops','Functions','Lists','Dictionaries','File Handling'], 'youtube': 'https://www.youtube.com/watch?v=rfscVS0vtbw'},
            {'title': 'Python Libraries', 'subtopics': ['Pandas: DataFrames, CSV, Cleaning','NumPy: Arrays, Operations, Indexing','Matplotlib: Plotting','Seaborn: Statistical plots'], 'youtube': 'https://www.youtube.com/watch?v=vmEHCJofslg'},
            {'title': 'Data Visualization', 'subtopics': ['Matplotlib','Seaborn','Data storytelling'], 'youtube': 'https://www.youtube.com/watch?v=3Xc3CA655Y4'},
            {'title': 'Machine Learning', 'subtopics': ['Supervised learning','Regression','Classification','Model evaluation','Scikit-learn'], 'youtube': 'https://www.youtube.com/watch?v=7eh4d6sabA0'},
        ],
        'projects': ['Sales prediction model','Movie recommendation system','Data dashboard','COVID data analysis']
    },
    'Web Development': {
        'steps': [
            {'title': 'HTML & CSS Fundamentals', 'subtopics': ['HTML5 elements','CSS selectors','Flexbox','Grid','Responsive design'], 'youtube': 'https://www.youtube.com/watch?v=qz0aGYrrlhU'},
            {'title': 'JavaScript Essentials', 'subtopics': ['DOM manipulation','Events','Fetch API','ES6+'], 'youtube': 'https://www.youtube.com/watch?v=W6NZfCO5SIk'},
            {'title': 'Frontend Frameworks', 'subtopics': ['React basics','Components','State management','Routing'], 'youtube': 'https://www.youtube.com/watch?v=bMknfKXIFA8'},
            {'title': 'Backend Basics', 'subtopics': ['Node.js / Flask','REST APIs','Databases','Deployment'], 'youtube': 'https://www.youtube.com/watch?v=Gd9YGbFYEbQ'},
        ],
        'projects': ['Portfolio website','E-commerce front page','Blog platform','REST API with Flask']
    },
    'Cybersecurity': {
        'steps': [
            {'title': 'Networking Fundamentals', 'subtopics': ['OSI Model','TCP/IP','DNS','HTTP/HTTPS'], 'youtube': 'https://www.youtube.com/watch?v=3QhU9jd03a0'},
            {'title': 'Linux & Command Line', 'subtopics': ['File system','Permissions','Bash scripting','SSH'], 'youtube': 'https://www.youtube.com/watch?v=sWbUDq4S6Y8'},
            {'title': 'Ethical Hacking Basics', 'subtopics': ['Reconnaissance','Scanning','Exploitation basics','Burp Suite'], 'youtube': 'https://www.youtube.com/watch?v=3Kq1MIfTWCE'},
            {'title': 'Cryptography & Defense', 'subtopics': ['Encryption algorithms','PKI','Firewalls','IDS/IPS'], 'youtube': 'https://www.youtube.com/watch?v=AQDCe585Lnc'},
        ],
        'projects': ['Network scanner','Password manager','CTF participation','Vulnerability report']
    },
    'Artificial Intelligence': {
        'steps': [
            {'title': 'Python for AI', 'subtopics': ['NumPy','Pandas','Data preprocessing'], 'youtube': 'https://www.youtube.com/watch?v=rfscVS0vtbw'},
            {'title': 'Machine Learning Core', 'subtopics': ['Linear regression','Decision trees','SVM','Cross-validation'], 'youtube': 'https://www.youtube.com/watch?v=7eh4d6sabA0'},
            {'title': 'Deep Learning', 'subtopics': ['Neural networks','TensorFlow/Keras','CNNs','RNNs'], 'youtube': 'https://www.youtube.com/watch?v=VyWAvY2CF9c'},
            {'title': 'NLP & Computer Vision', 'subtopics': ['Text processing','Transformers','Image classification','Object detection'], 'youtube': 'https://www.youtube.com/watch?v=X2vAabgKiWM'},
        ],
        'projects': ['Chatbot','Image classifier','Sentiment analyzer','AI game player']
    },
    'UI/UX Design': {
        'steps': [
            {'title': 'Design Fundamentals', 'subtopics': ['Color theory', 'Typography', 'Layout', 'Visual hierarchy'], 'youtube': 'https://www.youtube.com/watch?v=c9Wg6Cb_YlU'},
            {'title': 'UI Tools', 'subtopics': ['Figma', 'Adobe XD', 'Sketch', 'Prototyping'], 'youtube': 'https://www.youtube.com/watch?v=FTFaQWZBqQ8'},
            {'title': 'UX Research', 'subtopics': ['User personas', 'Wireframing', 'Usability testing'], 'youtube': 'https://www.youtube.com/watch?v=5QNWXZ_2d0Q'}
        ],
        'projects': ['Redesign a popular app', 'E-commerce checkout flow', 'Portfolio website design']
    },
    'Cloud Engineering': {
        'steps': [
            {'title': 'Cloud Fundamentals', 'subtopics': ['Virtualization', 'IaaS vs PaaS', 'Networking'], 'youtube': 'https://www.youtube.com/watch?v=M988_fsOSWo'},
            {'title': 'AWS Basics', 'subtopics': ['EC2', 'S3', 'IAM', 'VPC'], 'youtube': 'https://www.youtube.com/watch?v=3hLmDS179YE'},
            {'title': 'Infrastructure as Code', 'subtopics': ['Terraform', 'CloudFormation', 'Ansible'], 'youtube': 'https://www.youtube.com/watch?v=tomZWzslXw'}
        ],
        'projects': ['Host a static website on S3', 'Deploy a load-balanced app', 'Automate setup with Terraform']
    },
    'Internet of Things': {
        'steps': [
            {'title': 'Hardware Basics', 'subtopics': ['Microcontrollers', 'Sensors', 'Arduino', 'Raspberry Pi'], 'youtube': 'https://www.youtube.com/watch?v=nL34zDTPkcs'},
            {'title': 'IoT Platforms', 'subtopics': ['AWS IoT', 'MQTT', 'Edge Computing'], 'youtube': 'https://www.youtube.com/watch?v=UrHXOAib2s4'}
        ],
        'projects': ['Smart weather station', 'Home automation prototype']
    },
    'Mobile App Development': {
        'steps': [
            {'title': 'Mobile Basics', 'subtopics': ['UI guidelines', 'State management', 'REST APIs'], 'youtube': 'https://www.youtube.com/watch?v=fis26HvvDII'},
            {'title': 'Frameworks', 'subtopics': ['Flutter', 'React Native', 'Kotlin', 'Swift'], 'youtube': 'https://www.youtube.com/watch?v=VPvVD8t02U8'}
        ],
        'projects': ['To-Do app', 'Weather forecast app', 'Expense tracker']
    },
    'Software Development': {
        'steps': [
            {'title': 'Programming Basics', 'subtopics': ['Variables', 'OOP', 'Data Structures', 'Algorithms'], 'youtube': 'https://www.youtube.com/watch?v=8hly31xKli0'},
            {'title': 'Version Control', 'subtopics': ['Git', 'GitHub', 'Branching', 'Merging'], 'youtube': 'https://www.youtube.com/watch?v=RGOj5yH7evk'}
        ],
        'projects': ['CLI Task Manager', 'Simple web application']
    },
    'Product Management': {
        'steps': [
            {'title': 'Product Fundamentals', 'subtopics': ['Product lifecycle', 'Agile', 'Scrum'], 'youtube': 'https://www.youtube.com/watch?v=O12ZPo2j_N0'},
            {'title': 'Market Research', 'subtopics': ['Competitor analysis', 'User interviews', 'Roadmapping'], 'youtube': 'https://www.youtube.com/watch?v=ZfAzaCwGtyY'}
        ],
        'projects': ['Write a PRD', 'Conduct user interviews for an idea']
    }
}


def get_roadmap(domain):
    return ROADMAPS.get(domain, ROADMAPS['Software Development'])

def recommend_domain(interests, skills, subjects):
    scores = {}
    for domain, rules in DOMAIN_RULES.items():
        s = 0
        for i in interests:
            if i in rules['interests']: s += 3
        for sk in skills:
            if sk in rules['skills']: s += 2
        for sub in subjects:
            if sub in rules['subjects']: s += 1
        scores[domain] = s
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [r[0] for r in ranked[:3]] if ranked else ['Software Development']

def analyze_resume(filepath, domain):
    try:
        import PyPDF2
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ' '.join(page.extract_text() or '' for page in reader.pages).lower()
    except Exception:
        text = ''
        
    # NEW VALIDATION LOGIC
    validation_keywords = ['education', 'skills', 'projects', 'experience', 'objective', 'summary']
    if not any(k in text for k in validation_keywords):
        return -1, ["This document does not appear to be a valid resume. Please upload a proper resume containing sections like Education, Skills, Projects, or Experience."]

    keywords = {
        'Data Science': ['python','machine learning','pandas','numpy','sql','data','model'],
        'Web Development': ['html','css','javascript','react','api','flask','node'],
        'Cybersecurity': ['network','linux','security','firewall','encryption','penetration'],
        'Artificial Intelligence': ['neural','deep learning','tensorflow','keras','nlp','ai'],
    }
    kws = keywords.get(domain, keywords['Data Science'])
    hit = sum(1 for k in kws if k in text)
    base = int((hit / len(kws)) * 60) if kws else 0
    for bonus_word in ['github','project','internship','certification','achievement']:
        if bonus_word in text: base += 5
    score = min(base, 100)
    suggestions = []
    if score < 40:
        suggestions = ['Add quantifiable achievements', 'Include domain-specific keywords', 'Add GitHub project links', 'Improve section headings', 'Add an objective/summary section']
    elif score < 70:
        suggestions = ['Strengthen keyword density', 'Add measurable project outcomes', 'Include certifications', 'Optimize for ATS with clean formatting']
    else:
        suggestions = ['Polish action verbs', 'Add leadership/collaboration examples', 'Tailor for each application']
    return score, suggestions

COMPANIES = {
    'Cybersecurity': [
        {'name':'Google','url':'https://careers.google.com'},{'name':'Microsoft','url':'https://careers.microsoft.com'},
        {'name':'Amazon','url':'https://www.amazon.jobs'},{'name':'Cisco','url':'https://jobs.cisco.com'},
        {'name':'IBM','url':'https://www.ibm.com/careers'},{'name':'Palo Alto Networks','url':'https://jobs.paloaltonetworks.com'},
        {'name':'Deloitte','url':'https://www2.deloitte.com/careers'},{'name':'Intel','url':'https://jobs.intel.com'},
        {'name':'Oracle','url':'https://careers.oracle.com'},{'name':'Accenture','url':'https://www.accenture.com/careers'},
        {'name':'Capgemini','url':'https://www.capgemini.com/careers'},{'name':'TCS','url':'https://www.tcs.com/careers'},
        {'name':'Infosys','url':'https://www.infosys.com/careers'},{'name':'Wipro','url':'https://careers.wipro.com'},
        {'name':'Zoho','url':'https://careers.zoho.com'},
    ],
    'Data Science': [
        {'name':'Google','url':'https://careers.google.com'},{'name':'Microsoft','url':'https://careers.microsoft.com'},
        {'name':'Amazon','url':'https://www.amazon.jobs'},{'name':'Meta','url':'https://www.metacareers.com'},
        {'name':'Netflix','url':'https://jobs.netflix.com'},{'name':'IBM','url':'https://www.ibm.com/careers'},
        {'name':'Deloitte','url':'https://www2.deloitte.com/careers'},{'name':'Accenture','url':'https://www.accenture.com/careers'},
        {'name':'Capgemini','url':'https://www.capgemini.com/careers'},{'name':'TCS','url':'https://www.tcs.com/careers'},
        {'name':'Infosys','url':'https://www.infosys.com/careers'},{'name':'Wipro','url':'https://careers.wipro.com'},
        {'name':'Oracle','url':'https://careers.oracle.com'},{'name':'Zoho','url':'https://careers.zoho.com'},
        {'name':'Freshworks','url':'https://www.freshworks.com/company/careers'},
    ],
    'Web Development': [
        {'name':'Google','url':'https://careers.google.com'},{'name':'Microsoft','url':'https://careers.microsoft.com'},
        {'name':'Amazon','url':'https://www.amazon.jobs'},{'name':'Shopify','url':'https://www.shopify.com/careers'},
        {'name':'Atlassian','url':'https://www.atlassian.com/company/careers'},{'name':'Accenture','url':'https://www.accenture.com/careers'},
        {'name':'TCS','url':'https://www.tcs.com/careers'},{'name':'Infosys','url':'https://www.infosys.com/careers'},
        {'name':'Wipro','url':'https://careers.wipro.com'},{'name':'Zoho','url':'https://careers.zoho.com'},
        {'name':'Freshworks','url':'https://www.freshworks.com/company/careers'},{'name':'Capgemini','url':'https://www.capgemini.com/careers'},
        {'name':'IBM','url':'https://www.ibm.com/careers'},{'name':'Oracle','url':'https://careers.oracle.com'},
        {'name':'Deloitte','url':'https://www2.deloitte.com/careers'},
    ],
    'Artificial Intelligence': [
        {'name':'Google DeepMind','url':'https://deepmind.google/about/careers'},{'name':'OpenAI','url':'https://openai.com/careers'},
        {'name':'Microsoft','url':'https://careers.microsoft.com'},{'name':'Amazon','url':'https://www.amazon.jobs'},
        {'name':'Meta AI','url':'https://www.metacareers.com'},{'name':'NVIDIA','url':'https://www.nvidia.com/en-us/about-nvidia/careers'},
        {'name':'IBM','url':'https://www.ibm.com/careers'},{'name':'TCS','url':'https://www.tcs.com/careers'},
        {'name':'Infosys','url':'https://www.infosys.com/careers'},{'name':'Accenture','url':'https://www.accenture.com/careers'},
        {'name':'Wipro','url':'https://careers.wipro.com'},{'name':'Capgemini','url':'https://www.capgemini.com/careers'},
        {'name':'Oracle','url':'https://careers.oracle.com'},{'name':'Intel','url':'https://jobs.intel.com'},
        {'name':'Zoho','url':'https://careers.zoho.com'},
    ],
    'Cloud Engineering': [
        {'name':'AWS (Amazon)','url':'https://www.amazon.jobs'},{'name':'Microsoft Azure','url':'https://careers.microsoft.com'},
        {'name':'Google Cloud','url':'https://careers.google.com'},{'name':'IBM Cloud','url':'https://www.ibm.com/careers'},
        {'name':'Oracle Cloud','url':'https://careers.oracle.com'},{'name':'Accenture','url':'https://www.accenture.com/careers'},
        {'name':'TCS','url':'https://www.tcs.com/careers'},{'name':'Infosys','url':'https://www.infosys.com/careers'},
        {'name':'Wipro','url':'https://careers.wipro.com'},{'name':'Capgemini','url':'https://www.capgemini.com/careers'},
        {'name':'Deloitte','url':'https://www2.deloitte.com/careers'},{'name':'Cisco','url':'https://jobs.cisco.com'},
        {'name':'VMware','url':'https://careers.vmware.com'},{'name':'Zoho','url':'https://careers.zoho.com'},
        {'name':'Freshworks','url':'https://www.freshworks.com/company/careers'},
    ],
}
for d in ['Internet of Things','UI/UX Design','Mobile App Development','Software Development','Product Management']:
    COMPANIES[d] = COMPANIES['Web Development']

SKILL_RESOURCES = {
    'SQL': {'youtube': 'https://www.youtube.com/watch?v=HXV3zeQKqGY', 'project': 'Build a sales analytics dashboard using SQLite'},
    'Data Visualization': {'youtube': 'https://www.youtube.com/watch?v=3Xc3CA655Y4', 'project': 'Create an interactive data dashboard with Matplotlib'},
    'Machine Learning': {'youtube': 'https://www.youtube.com/watch?v=7eh4d6sabA0', 'project': 'Build a movie recommendation engine'},
    'Python': {'youtube': 'https://www.youtube.com/watch?v=rfscVS0vtbw', 'project': 'Build a CLI task manager in Python'},
    'JavaScript': {'youtube': 'https://www.youtube.com/watch?v=W6NZfCO5SIk', 'project': 'Build a to-do web app with vanilla JS'},
    'Cloud Platforms': {'youtube': 'https://www.youtube.com/watch?v=M988_fsOSWo', 'project': 'Deploy a Flask app on AWS Free Tier'},
    'Networking': {'youtube': 'https://www.youtube.com/watch?v=3QhU9jd03a0', 'project': 'Set up a home lab network with VirtualBox'},
    'Linux': {'youtube': 'https://www.youtube.com/watch?v=sWbUDq4S6Y8', 'project': 'Automate system tasks with Bash scripts'},
    'API Development': {'youtube': 'https://www.youtube.com/watch?v=Gd9YGbFYEbQ', 'project': 'Build a REST API with Flask and SQLite'},
    'Git and GitHub': {'youtube': 'https://www.youtube.com/watch?v=RGOj5yH7evk', 'project': 'Contribute to an open-source project on GitHub'},
    'UI/UX Design': {'youtube': 'https://www.youtube.com/watch?v=c9Wg6Cb_YlU', 'project': 'Design a mobile app prototype in Figma'},
    'Figma': {'youtube': 'https://www.youtube.com/watch?v=FTFaQWZBqQ8', 'project': 'Create a high-fidelity prototype with auto layout'},
    'C++': {'youtube': 'https://www.youtube.com/watch?v=vLnPwxZdW4Y', 'project': 'Build a simple student record system in C++'},
    'Java': {'youtube': 'https://www.youtube.com/watch?v=eIrMbAQSU34', 'project': 'Build a banking console application in Java'},
    'HTML': {'youtube': 'https://www.youtube.com/watch?v=qz0aGYrrlhU', 'project': 'Build your personal portfolio website'},
    'CSS': {'youtube': 'https://www.youtube.com/watch?v=1Rs2ND1ryYc', 'project': 'Style a landing page with animations'},
}

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name','Student')
        degree = request.form.get('degree','')
        with get_db() as conn:
            cur = conn.execute('INSERT INTO students (name, degree) VALUES (?,?)', (name, degree))
            session['student_id'] = cur.lastrowid
        session['name'] = name
        session['degree'] = degree
        return render_template('index.html', welcome=True, name=name, degree=degree)
    return render_template('index.html', welcome=False)

@app.route('/assessment', methods=['GET','POST'])
def assessment():
    if request.method == 'POST':
        interests = request.form.getlist('interests')
        subjects = request.form.getlist('subjects')
        skills = request.form.getlist('skills')
        personality = request.form.get('personality','')
        domains = recommend_domain(interests, skills, subjects)
        domain = domains[0] if domains else 'Data Science'
        student_id = session.get('student_id', 1)
        with get_db() as conn:
            conn.execute('INSERT INTO assessments (student_id,interests,subjects,skills,personality,domain) VALUES (?,?,?,?,?,?)',
                (student_id, json.dumps(interests), json.dumps(subjects), json.dumps(skills), personality, domain))
        session['domain'] = domain
        session['domains'] = domains
        session['skills'] = skills
        return render_template('assessment.html', submitted=True, domains=domains, domain=domain,
                               interests=interests, skills=skills, subjects=subjects, personality=personality)
    return render_template('assessment.html', submitted=False)

@app.route('/roadmap')
@app.route('/roadmap/<path:domain>')
def roadmap(domain=None):
    if not domain: domain = session.get('domain','Data Science')
    data = get_roadmap(domain)
    all_domains = list(ROADMAPS.keys())
    return render_template('roadmap.html', domain=domain, steps=data['steps'], projects=data['projects'], all_domains=all_domains)

@app.route('/resume', methods=['GET','POST'])
def resume():
    result = None
    if request.method == 'POST':
        domain = session.get('domain','Data Science')
        f = request.files.get('resume')
        if f and f.filename.endswith('.pdf'):
            fname = secure_filename(f.filename)
            fpath = os.path.join(app.config['UPLOAD_FOLDER'], fname)
            f.save(fpath)
            score, suggestions = analyze_resume(fpath, domain)
            if score == -1:
                flash(suggestions[0], 'error')
            else:
                student_id = session.get('student_id', 1)
                with get_db() as conn:
                    conn.execute('INSERT INTO resume_analyses (student_id,score,suggestions) VALUES (?,?,?)',
                        (student_id, score, json.dumps(suggestions)))
                session['resume_score'] = score
                result = {'score': score, 'suggestions': suggestions, 'domain': domain}
        else:
            flash('Please upload a valid PDF file.', 'error')
    return render_template('resume.html', result=result)

@app.route('/companies')
def companies():
    domain = request.args.get('domain', session.get('domain','Data Science'))
    all_domains = list(COMPANIES.keys())
    company_list = COMPANIES.get(domain, COMPANIES['Data Science'])
    return render_template('companies.html', domain=domain, companies=company_list, all_domains=all_domains)

@app.route('/benchmark')
def benchmark():
    resume_score = session.get('resume_score', 0)
    user_skills = session.get('skills', [])
    goals = session.get('short_term', '') + session.get('long_term', '')
    
    modules_pts = 15 + (15 if goals else 0)
    projects_pts = 10 + min(len(user_skills)*2, 20)
    resume_pts = int((resume_score / 100) * 20)
    skill_pts = min(len(user_skills)*2, 20)
    
    total_score = modules_pts + projects_pts + resume_pts + skill_pts
    level = 'Beginner' if total_score <= 40 else ('Intermediate' if total_score <= 70 else 'Interview Ready')
    return render_template('benchmark.html', score=total_score, level=level,
                           modules=modules_pts, projects=projects_pts, 
                           resume=resume_pts, tests=skill_pts)

@app.route('/skills')
def skills():
    domain = session.get('domain','Data Science')
    user_skills = session.get('skills', [])
    domain_required = {
        'Data Science': ['Python','SQL','Machine Learning','Data Visualization'],
        'Web Development': ['HTML','CSS','JavaScript','API Development'],
        'Cybersecurity': ['Linux','Networking','Python'],
        'Artificial Intelligence': ['Python','Machine Learning'],
        'Cloud Engineering': ['Cloud Platforms','Linux','API Development'],
        'UI/UX Design': ['UI/UX Design', 'Figma'],
    }
    required = domain_required.get(domain, ['Python','Git and GitHub'])
    missing = [s for s in required if s not in user_skills]
    missing_data = [{'skill': s, **SKILL_RESOURCES.get(s, {'youtube':'https://youtube.com','project':'Build a practice project'})} for s in missing]
    return render_template('skills.html', domain=domain, missing_skills=missing_data, all_skills=SKILL_RESOURCES)

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    student_id = session.get('student_id', 1)
    if request.method == 'POST':
        short_term = request.form.get('short_term','')
        long_term = request.form.get('long_term','')
        with get_db() as conn:
            conn.execute('INSERT INTO goals (student_id,short_term,long_term) VALUES (?,?,?)', (student_id, short_term, long_term))
        session['short_term'] = short_term
        session['long_term'] = long_term
    goals = {'short_term': session.get('short_term',''), 'long_term': session.get('long_term','')}
    domain = session.get('domain','Data Science')
    user_skills = session.get('skills', [])
    resume_score = session.get('resume_score', 0)
    all_skills = ['Python','JavaScript','SQL','Machine Learning','Data Visualization','UI/UX Design','Figma','Git and GitHub','Linux','Networking','Cloud Platforms','API Development','C++','Java','HTML','CSS']
    skill_scores = [85 if s in user_skills else 20 for s in all_skills[:8]]
    skill_labels = all_skills[:8]
    return render_template('dashboard.html', name=session.get('name','Student'), domain=domain,
                           resume_score=resume_score, goals=goals,
                           skill_labels=skill_labels, skill_scores=skill_scores)

DAILY_QA = {
    'UI/UX Design': [
        {'q': 'What is the primary purpose of wireframing?', 'options': ['Adding final colors', 'Determining structural layout', 'Writing backend code', 'Animating buttons'], 'answer': 'Determining structural layout', 'explanation': 'Wireframing focuses on structure and layout without visual distractions like color or typography.'},
        {'q': 'Which Figma feature automatically adjusts padding and spacing?', 'options': ['Variants', 'Components', 'Auto Layout', 'Masking'], 'answer': 'Auto Layout', 'explanation': 'Auto Layout lets you create dynamic designs that grow or shrink as you change content.'},
        {'q': 'What does "UX" stand for?', 'options': ['User Exception', 'Universal XML', 'User Experience', 'Utility Exchange'], 'answer': 'User Experience', 'explanation': 'UX refers to the overall experience a person has when interacting with a product.'},
        {'q': 'Which color theory concept involves colors opposite each other on the color wheel?', 'options': ['Analogous', 'Monochromatic', 'Complementary', 'Triadic'], 'answer': 'Complementary', 'explanation': 'Complementary colors create high contrast when placed next to each other.'},
        {'q': 'What is a "Persona" in UX design?', 'options': ['A target user proxy', 'A CSS framework', 'A font family', 'A background color'], 'answer': 'A target user proxy', 'explanation': 'Personas are fictional characters created to represent different user types.'}
    ],
    'Software Development': [
        {'q': 'What does OOP stand for?', 'options': ['Object-Oriented Programming', 'Out Of Process', 'Only One Purpose', 'Object Oriented Protocol'], 'answer': 'Object-Oriented Programming', 'explanation': 'OOP is a programming paradigm based on the concept of "objects".'},
        {'q': 'Which data structure uses LIFO?', 'options': ['Queue', 'Linked List', 'Stack', 'Tree'], 'answer': 'Stack', 'explanation': 'Stack uses Last-In-First-Out (LIFO) method for adding/removing items.'},
        {'q': 'What is Git?', 'options': ['Programming Language', 'Version Control System', 'Web Browser', 'Database'], 'answer': 'Version Control System', 'explanation': 'Git is used to track changes in source code during software development.'},
        {'q': 'What does a "for" loop do?', 'options': ['Executes code once', 'Iterates over a sequence', 'Defines a function', 'Handles errors'], 'answer': 'Iterates over a sequence', 'explanation': 'A for loop is used for iterating over a sequence (like a list or string).'},
        {'q': 'What is the purpose of an API?', 'options': ['Styling websites', 'Storing data securely', 'Communication between software', 'Debugging code'], 'answer': 'Communication between software', 'explanation': 'APIs allow different applications to communicate and share data.'}
    ]
}

@app.route('/daily_practice', methods=['POST'])
def daily_practice():
    domain = session.get('domain', 'Software Development')
    questions = DAILY_QA.get(domain, DAILY_QA['Software Development'])
    
    score = 0
    results = []
    
    for i, q in enumerate(questions):
        user_answer = request.form.get(f'q_{i}')
        is_correct = user_answer == q['answer']
        if is_correct:
            score += 1
            
        results.append({
            'question': q['q'],
            'user_answer': user_answer,
            'correct_answer': q['answer'],
            'is_correct': is_correct,
            'explanation': q['explanation']
        })
        
    return render_template('daily_practice_result.html', score=score, total=len(questions), results=results, domain=domain)

@app.route('/daily_practice')
def daily_practice_view():
    domain = session.get('domain', 'Software Development')
    questions = DAILY_QA.get(domain, DAILY_QA['Software Development'])
    return render_template('daily_practice.html', questions=questions, domain=domain)

import os

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
