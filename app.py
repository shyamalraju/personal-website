from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from markupsafe import escape
import os
from werkzeug.utils import secure_filename
import plotly
import plotly.graph_objs as go
import json
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'static/images')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ADMIN_PIN'] = os.environ.get('ADMIN_PIN', '1234')  # Change this in production

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    # Debug print
    print("Admin login attempt - Current session:", session)
    
    if request.method == 'POST':
        pin = request.form.get('pin')
        if pin == app.config['ADMIN_PIN']:
            session['is_admin'] = True
            print("Admin login successful")
            return redirect(url_for('upload_profile'))
        print("Admin login failed")
        return render_template('admin_login.html', error=True)
    return render_template('admin_login.html', error=False)

@app.route('/upload-profile', methods=['GET', 'POST'])
@admin_required
def upload_profile():
    if request.method == 'GET':
        return render_template('upload_profile.html')
    
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return redirect(url_for('index'))
            
    return redirect(request.url)

def create_pie_chart():
    # Sample data for the pie chart
    labels = ['Python', 'JavaScript/TypeScript', 'HTML', 'CSS', 'SQL']
    values = [40, 25, 15, 15, 5]
    
    # Create the pie chart
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.3,
        marker=dict(colors=['#3B82F6', '#F7DF1E', '#E34F26', '#1572B6', '#336791']),
        hovertemplate="<b>%{label}</b><br>" +
                      "%{percent}<br>" +
                      "<extra></extra>"
    )])
    
    # Update the layout for dark theme
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff'),
        margin=dict(t=0, b=0, l=0, r=0),
        showlegend=True,
        legend=dict(
            orientation="h",  # horizontal orientation
            yanchor="bottom",
            y=-0.2,  # position below the chart
            xanchor="center",
            x=0.5,  # centered
            font=dict(color='#ffffff'),
            bgcolor='rgba(0,0,0,0)'
        )
    )
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

@app.route('/')
def index():
    # Debug print
    print("Current session:", session)
    print("Is admin?", session.get('is_admin'))
    
    # Get the pie chart JSON
    pie_chart = create_pie_chart()
    return render_template('index.html', pie_chart=pie_chart)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/projects')
def projects():
    # Example project data
    projects = [
        {
            'title': 'Project 1',
            'description': 'A web application built with Flask and TailwindCSS',
            'tech_stack': ['Python', 'Flask', 'TailwindCSS']
        },
        {
            'title': 'Project 2',
            'description': 'Mobile app development using React Native',
            'tech_stack': ['JavaScript', 'React Native', 'Redux']
        },
        {
            'title': 'Project 3',
            'description': 'Machine Learning project for image classification',
            'tech_stack': ['Python', 'TensorFlow', 'OpenCV']
        }
    ]
    return render_template('projects.html', projects=projects)

@app.route('/blog')
def blog():
    # Example blog posts
    posts = [
        {
            'title': 'Getting Started with Flask',
            'date': 'March 15, 2024',
            'preview': 'Learn how to build web applications with Flask, a lightweight Python web framework...',
            'read_time': '5 min read',
            'tags': ['Python', 'Web Development', 'Flask']
        },
        {
            'title': 'Mastering TailwindCSS',
            'date': 'March 10, 2024',
            'preview': 'Discover the power of utility-first CSS and how to build modern interfaces...',
            'read_time': '4 min read',
            'tags': ['CSS', 'TailwindCSS', 'Frontend']
        },
        {
            'title': 'Data Visualization with Plotly',
            'date': 'March 5, 2024',
            'preview': 'Create interactive and beautiful data visualizations using Plotly...',
            'read_time': '6 min read',
            'tags': ['Python', 'Data Science', 'Plotly']
        }
    ]
    return render_template('blog.html', posts=posts)

@app.route('/admin-logout')
def admin_logout():
    # Clear the entire session instead of just popping one key
    session.clear()
    print("Admin logged out - Session cleared")
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Try a different port (5001)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))